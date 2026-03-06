export const prerender = false

import type { APIRoute } from 'astro'
import { createServiceClient } from '../../../lib/db/client'

/**
 * POST /api/ficha/:token
 * Handles ficha técnica form submission (multipart/form-data).
 * - Validates token, expiry, and status
 * - Parses credits from form field naming convention: credits[role][index][field]
 * - Uploads filmmaker photo + credit photos to Supabase Storage
 * - Stores credits as JSONB, updates status to ficha_received
 */
export const POST: APIRoute = async ({ params, request }) => {
  const { token } = params
  if (!token) {
    return json({ error: 'Missing token' }, 400)
  }

  const db = createServiceClient()

  // 1. Validate token
  const { data: sub, error: fetchErr } = await db
    .from('film_submissions')
    .select('*')
    .eq('ficha_token', token)
    .maybeSingle()

  if (fetchErr || !sub) {
    return json({ error: 'Invalid or expired token' }, 404)
  }

  if (sub.status === 'published') {
    return json({ error: 'This work has already been published.' }, 400)
  }

  if (sub.status === 'ficha_received') {
    return json({ error: 'Ficha already submitted.' }, 400)
  }

  const isExpired = sub.ficha_token_expires_at && new Date(sub.ficha_token_expires_at) < new Date()
  if (isExpired) {
    return json({ error: 'This link has expired. Contact the PRISMA team for a new one.' }, 400)
  }

  // 2. Parse multipart form data
  let formData: FormData
  try {
    formData = await request.formData()
  } catch {
    return json({ error: 'Invalid form data' }, 400)
  }

  // 3. Parse credits from flat FormData keys
  //    Pattern: credits[role][index][field] = value
  //    Also: credits[role][index][also][otherRole] = "on"
  const credits = parseCredits(formData)

  // 4. Upload photos to Supabase Storage
  const submissionId = String(sub.id)
  const bucket = 'filmmaker-assets'

  // Upload filmmaker photo
  let filmmakerPhotoUrl: string | null = null
  const filmmakerPhoto = formData.get('filmmaker_photo')
  if (filmmakerPhoto && filmmakerPhoto instanceof File && filmmakerPhoto.size > 0) {
    filmmakerPhotoUrl = await uploadFile(db, bucket, `submissions/${submissionId}/filmmaker`, filmmakerPhoto)
  }

  // Upload credit photos
  for (const role of Object.keys(credits)) {
    for (const entry of credits[role]) {
      if (entry._photoFile && entry._photoFile instanceof File && entry._photoFile.size > 0) {
        const slug = slugify(entry.name || 'unknown')
        const path = `submissions/${submissionId}/credits/${role}/${slug}`
        entry.photo_url = await uploadFile(db, bucket, path, entry._photoFile)
      }
      delete entry._photoFile
    }
  }

  // 5. Collect text fields
  const bioFull = formStr(formData, 'bio_full')
  const filmmakerWebsite = formStr(formData, 'filmmaker_website')
  const filmmakerInstagram = formStr(formData, 'filmmaker_instagram')
  const countries = formStr(formData, 'countries')
  const languages = formStr(formData, 'languages')
  const genres = formStr(formData, 'genres')
  const synopsisFull = formStr(formData, 'synopsis_full')

  // 6. Update film_submissions
  const { error: updateErr } = await db
    .from('film_submissions')
    .update({
      status: 'ficha_received',
      ficha_submitted_at: new Date().toISOString(),
      ficha_credits: credits,
      ficha_bio_full: bioFull || null,
      ficha_filmmaker_photo: filmmakerPhotoUrl || null,
      ficha_filmmaker_website: filmmakerWebsite || null,
      ficha_filmmaker_instagram: filmmakerInstagram || null,
      ficha_countries: countries ? splitComma(countries) : null,
      ficha_languages: languages ? splitComma(languages) : null,
      ficha_genres: genres ? splitComma(genres) : null,
      ficha_synopsis_full: synopsisFull || null,
    } as any)
    .eq('id', sub.id)

  if (updateErr) {
    console.error('[ficha] update error:', updateErr.message)
    return json({ error: 'Error saving ficha. Please try again.' }, 500)
  }

  return json({ success: true })
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function json(data: Record<string, any>, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function formStr(formData: FormData, key: string): string {
  const val = formData.get(key)
  return typeof val === 'string' ? val.trim() : ''
}

function splitComma(str: string): string[] {
  return str.split(',').map(s => s.trim()).filter(Boolean)
}

function slugify(str: string): string {
  return str
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 60)
}

/**
 * Parse credits from FormData.
 * Keys like: credits[director][0][name], credits[director][0][photo], credits[director][0][also][writer]
 * Returns: { director: [{ name, bio, also: ['writer'], _photoFile }], ... }
 */
function parseCredits(formData: FormData): Record<string, any[]> {
  const credits: Record<string, Record<number, any>> = {}
  const creditRegex = /^credits\[(\w+)\]\[(\d+)\]\[(\w+)\](?:\[(\w+)\])?$/

  for (const [key, value] of formData.entries()) {
    const match = key.match(creditRegex)
    if (!match) continue

    const [, role, idxStr, field, subField] = match
    const idx = parseInt(idxStr, 10)

    if (!credits[role]) credits[role] = {}
    if (!credits[role][idx]) credits[role][idx] = { name: '', bio: '', also: [], photo_url: null }

    if (field === 'also' && subField) {
      // Checkbox — value is "on"
      if (value === 'on') {
        credits[role][idx].also.push(subField)
      }
    } else if (field === 'photo') {
      // File upload
      if (value instanceof File && value.size > 0) {
        credits[role][idx]._photoFile = value
      }
    } else if (field === 'name') {
      credits[role][idx].name = typeof value === 'string' ? value.trim() : ''
    } else if (field === 'bio') {
      credits[role][idx].bio = typeof value === 'string' ? value.trim() : ''
    }
  }

  // Convert indexed objects to arrays, filter out entries with no name
  const result: Record<string, any[]> = {}
  for (const role of Object.keys(credits)) {
    const entries = Object.values(credits[role]).filter(e => e.name)
    if (entries.length > 0) {
      result[role] = entries
    }
  }
  return result
}

/**
 * Upload a file to Supabase Storage.
 * Returns the public URL or null on failure.
 */
async function uploadFile(
  db: ReturnType<typeof createServiceClient>,
  bucket: string,
  pathPrefix: string,
  file: File
): Promise<string | null> {
  try {
    const ext = file.name.split('.').pop()?.toLowerCase() || 'jpg'
    const filePath = `${pathPrefix}.${ext}`

    const { error } = await db.storage.from(bucket).upload(filePath, file, {
      contentType: file.type || 'image/jpeg',
      upsert: true,
    })

    if (error) {
      console.error(`[ficha] upload error for ${filePath}:`, error.message)
      return null
    }

    const { data: urlData } = db.storage.from(bucket).getPublicUrl(filePath)
    return urlData?.publicUrl || null
  } catch (err) {
    console.error(`[ficha] upload exception:`, err)
    return null
  }
}
