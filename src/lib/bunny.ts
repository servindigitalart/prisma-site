/**
 * src/lib/bunny.ts
 * ─────────────────
 * Bunny Stream API client — server-side only.
 *
 * Uses env vars:
 *   BUNNY_API_KEY        – Stream library API key
 *   BUNNY_LIBRARY_ID     – Stream library numeric ID
 *   BUNNY_CDN_HOSTNAME   – CDN pull zone hostname (vz-xxx.b-cdn.net)
 *   BUNNY_SECURITY_KEY   – Token auth security key for signed URLs
 */

import { createHash } from 'crypto'

const BUNNY_API_KEY = import.meta.env.BUNNY_API_KEY
const BUNNY_LIBRARY_ID = import.meta.env.BUNNY_LIBRARY_ID
const BUNNY_CDN_HOSTNAME = import.meta.env.BUNNY_CDN_HOSTNAME
const BUNNY_SECURITY_KEY = import.meta.env.BUNNY_SECURITY_KEY

// ── Create a video entry in Bunny (returns videoId GUID) ──────────────────────

export async function createBunnyVideo(title: string): Promise<string> {
  const res = await fetch(
    `https://video.bunnycdn.com/library/${BUNNY_LIBRARY_ID}/videos`,
    {
      method: 'POST',
      headers: {
        'AccessKey': BUNNY_API_KEY,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title }),
    }
  )

  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Bunny createVideo failed (${res.status}): ${text}`)
  }

  const data = await res.json()
  return data.guid as string
}

// ── Get the tus-compatible upload URL for a video ─────────────────────────────

export function getBunnyUploadUrl(videoId: string): string {
  return `https://video.bunnycdn.com/library/${BUNNY_LIBRARY_ID}/videos/${videoId}`
}

// ── Generate SHA256 token for signed embed URL ────────────────────────────────

export function generateBunnyToken(videoId: string): { token: string; expires: number } {
  const expires = Math.floor(Date.now() / 1000) + 14400 // 4 hours
  const token = createHash('sha256')
    .update(BUNNY_SECURITY_KEY + videoId + String(expires))
    .digest('hex')
  return { token, expires }
}

// ── Signed iframe embed URL (4-hour expiry) ───────────────────────────────────

export function getBunnyEmbedUrlSigned(videoId: string): string {
  const { token, expires } = generateBunnyToken(videoId)
  return `https://iframe.mediadelivery.net/embed/${BUNNY_LIBRARY_ID}/${videoId}?token=${token}&expires=${expires}&autoplay=false&preload=false`
}

// ── Unsigned embed URL (for public/non-token-auth libraries) ──────────────────

export function getBunnyEmbedUrl(videoId: string): string {
  return `https://iframe.mediadelivery.net/embed/${BUNNY_LIBRARY_ID}/${videoId}?autoplay=false&preload=false`
}

// ── Get video status / metadata from Bunny ────────────────────────────────────

export async function getBunnyVideoStatus(videoId: string): Promise<Record<string, any>> {
  const res = await fetch(
    `https://video.bunnycdn.com/library/${BUNNY_LIBRARY_ID}/videos/${videoId}`,
    { headers: { 'AccessKey': BUNNY_API_KEY } }
  )

  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Bunny getVideoStatus failed (${res.status}): ${text}`)
  }

  return res.json()
}

// ── Delete a video from Bunny ─────────────────────────────────────────────────

export async function deleteBunnyVideo(videoId: string): Promise<void> {
  const res = await fetch(
    `https://video.bunnycdn.com/library/${BUNNY_LIBRARY_ID}/videos/${videoId}`,
    { method: 'DELETE', headers: { 'AccessKey': BUNNY_API_KEY } }
  )

  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Bunny deleteVideo failed (${res.status}): ${text}`)
  }
}
