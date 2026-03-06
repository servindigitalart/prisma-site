export const prerender = false

import type { APIRoute } from 'astro'
import { requireAdmin } from '../../../../lib/admin'
import { createServiceClient } from '../../../../lib/db/client'

/**
 * POST /api/admin/publish/:id
 * Creates work + people + work_people records from a ficha-received submission.
 * Body: { slug: string, work_type: string, people: [{ person_id, name, role, also_roles }] }
 */
export const POST: APIRoute = async ({ params, request, locals }) => {
  const isAdmin = await requireAdmin(locals)
  if (!isAdmin) {
    return json({ error: 'Forbidden' }, 403)
  }

  const submissionId = Number(params.id)
  if (!submissionId || isNaN(submissionId)) {
    return json({ error: 'Invalid submission ID' }, 400)
  }

  let body: any
  try {
    body = await request.json()
  } catch {
    return json({ error: 'Invalid JSON body' }, 400)
  }

  const { slug, work_type, people } = body

  if (!slug || typeof slug !== 'string') {
    return json({ error: 'Missing or invalid slug' }, 400)
  }

  if (!work_type || !['film', 'short', 'series', 'music_video'].includes(work_type)) {
    return json({ error: 'Invalid work_type' }, 400)
  }

  if (!Array.isArray(people) || people.length === 0) {
    return json({ error: 'At least one person is required' }, 400)
  }

  const db = createServiceClient()

  // 1. Fetch the submission
  const { data: sub, error: fetchErr } = await db
    .from('film_submissions')
    .select('*')
    .eq('id', submissionId)
    .maybeSingle()

  if (fetchErr || !sub) {
    return json({ error: 'Submission not found' }, 404)
  }

  if (sub.status === 'published') {
    return json({ error: 'Already published' }, 400)
  }

  const workId = `work_${slug}`

  // Cast sub to any to access ficha columns (not in generated types yet)
  const ficha = sub as any

  // 2. Check work ID doesn't already exist
  const { data: existingWork } = await db
    .from('works')
    .select('id')
    .eq('id', workId)
    .maybeSingle()

  if (existingWork) {
    return json({ error: `Work ID "${workId}" already exists. Choose a different slug.` }, 409)
  }

  try {
    // 3. Create the work record
    const workInsert: Record<string, any> = {
      id: workId,
      title: sub.title,
      type: work_type,
      year: sub.year || null,
      duration_min: sub.runtime_min || null,
      synopsis: ficha.ficha_synopsis_full || sub.synopsis || null,
      countries: ficha.ficha_countries || sub.countries || [],
      languages: ficha.ficha_languages || sub.languages || [],
      genres: ficha.ficha_genres || sub.genres || [],
      is_published: true,
    }

    const { error: workErr } = await db.from('works').insert(workInsert)

    if (workErr) {
      console.error('[publish] work insert error:', workErr.message)
      return json({ error: `Failed to create work: ${workErr.message}` }, 500)
    }

    // 4. Upsert people and create work_people entries
    const validRoles = ['director', 'cinematography', 'actor', 'writer', 'editor', 'composer', 'production_design']
    let billingOrder = 0

    for (const person of people) {
      const { person_id, name, role, also_roles } = person

      if (!person_id || !name || !role) {
        console.warn('[publish] skipping person with missing data:', person)
        continue
      }

      // Get bio + profile_path from ficha credits if available
      let personBio: string | null = null
      let personPhoto: string | null = null
      const fichaCredits: Record<string, any[]> = ficha.ficha_credits || {}

      // Search through ficha credits for this person's data
      for (const [, entries] of Object.entries(fichaCredits)) {
        for (const entry of entries) {
          if (entry.name && entry.name.trim().toLowerCase() === name.trim().toLowerCase()) {
            personBio = entry.bio || null
            personPhoto = entry.photo_url || null
            break
          }
        }
        if (personBio || personPhoto) break
      }

      // Upsert person (don't overwrite existing data)
      const { data: existingPerson } = await db
        .from('people')
        .select('id')
        .eq('id', person_id)
        .maybeSingle()

      if (!existingPerson) {
        const personInsert: Record<string, any> = {
          id: person_id,
          name: name.trim(),
        }
        if (personBio) personInsert.bio = personBio
        if (personPhoto) personInsert.profile_path = personPhoto

        const { error: personErr } = await db.from('people').insert(personInsert)
        if (personErr) {
          console.error(`[publish] person insert error for ${person_id}:`, personErr.message)
          // Continue with other people instead of failing entirely
        }
      }

      // Create work_people for the primary role
      if (validRoles.includes(role)) {
        billingOrder++
        const { error: wpErr } = await db.from('work_people').insert({
          work_id: workId,
          person_id: person_id,
          role: role as any,
          billing_order: billingOrder,
        })
        if (wpErr) {
          console.error(`[publish] work_people insert error (${person_id}, ${role}):`, wpErr.message)
        }
      }

      // Create work_people for also_roles
      if (Array.isArray(also_roles)) {
        for (const alsoRole of also_roles) {
          if (validRoles.includes(alsoRole)) {
            billingOrder++
            const { error: wpAlsoErr } = await db.from('work_people').insert({
              work_id: workId,
              person_id: person_id,
              role: alsoRole as any,
              billing_order: billingOrder,
            })
            if (wpAlsoErr) {
              console.error(`[publish] work_people also insert error (${person_id}, ${alsoRole}):`, wpAlsoErr.message)
            }
          }
        }
      }
    }

    // 5. Update submission status to published
    const { error: statusErr } = await db
      .from('film_submissions')
      .update({
        status: 'published',
        work_id: workId,
        published_at: new Date().toISOString(),
      } as any)
      .eq('id', submissionId)

    if (statusErr) {
      console.error('[publish] status update error:', statusErr.message)
      // Work was already created, so we continue
    }

    return json({
      success: true,
      work_id: workId,
      slug: slug,
      people_count: people.length,
    })

  } catch (err) {
    console.error('[publish] unexpected error:', err)
    return json({ error: 'Internal server error during publishing' }, 500)
  }
}

function json(data: Record<string, any>, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}
