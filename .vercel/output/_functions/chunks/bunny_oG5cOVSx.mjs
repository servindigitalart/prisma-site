import { createHash } from 'crypto';

const BUNNY_API_KEY = "";
const BUNNY_LIBRARY_ID = "";
const BUNNY_SECURITY_KEY = "8a7b4ddc-4dee-4c7a-afb7-ca1cbb3a8773";
async function createBunnyVideo(title) {
  const res = await fetch(
    `https://video.bunnycdn.com/library/${BUNNY_LIBRARY_ID}/videos`,
    {
      method: "POST",
      headers: {
        "AccessKey": BUNNY_API_KEY,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ title })
    }
  );
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Bunny createVideo failed (${res.status}): ${text}`);
  }
  const data = await res.json();
  return data.guid;
}
function getBunnyUploadUrl(videoId) {
  return `https://video.bunnycdn.com/library/${BUNNY_LIBRARY_ID}/videos/${videoId}`;
}
function generateBunnyToken(videoId) {
  const expires = Math.floor(Date.now() / 1e3) + 14400;
  const token = createHash("sha256").update(BUNNY_SECURITY_KEY + videoId + String(expires)).digest("hex");
  return { token, expires };
}
function getBunnyEmbedUrlSigned(videoId) {
  const { token, expires } = generateBunnyToken(videoId);
  return `https://iframe.mediadelivery.net/embed/${BUNNY_LIBRARY_ID}/${videoId}?token=${token}&expires=${expires}&autoplay=false&preload=false`;
}

export { getBunnyEmbedUrlSigned as a, createBunnyVideo as c, getBunnyUploadUrl as g };
