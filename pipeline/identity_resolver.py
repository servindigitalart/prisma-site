#!/usr/local/bin/python3
"""
Canonical identity resolution for people using tmdb_id as canonical key.
"""
from typing import Any
from supabase import Client  # type: ignore


class PersonIdentityResolver:
    """
    Resolve person identities using tmdb_id (canonical) instead of slug.
    
    Usage:
        resolver = PersonIdentityResolver(supabase_client)
        canonical_id = resolver.resolve_or_create(
            tmdb_id=4,
            name="Buster Keaton",
            slug="person_buster-keaton",
            profile_data={...}
        )
    """
    
    def __init__(self, client: Client):
        self.client = client
        self._cache: dict[int, str] = {}  # tmdb_id → person_id
    
    def resolve_or_create(
        self,
        tmdb_id: int | None,
        name: str,
        slug: str,
        profile_data: dict[str, Any],
    ) -> str:
        """
        Resolve person identity by tmdb_id.
        
        Args:
            tmdb_id: TMDB person ID (canonical key)
            name: Person name
            slug: Proposed person_id (may be adjusted)
            profile_data: Full person record
        
        Returns:
            Canonical person_id from database
        """
        # No tmdb_id → use slug as-is
        if tmdb_id is None:
            return self._upsert_by_slug(slug, profile_data)
        
        # Check cache
        if tmdb_id in self._cache:
            return self._cache[tmdb_id]
        
        # Query by tmdb_id (canonical key)
        result = self.client.table("people").select("id").eq("tmdb_id", tmdb_id).execute()
        
        if result.data and len(result.data) > 0:
            # Person exists — return existing person_id
            person_id = result.data[0]["id"]
            self._cache[tmdb_id] = person_id
            
            # Update with latest data
            self.client.table("people").update(profile_data).eq("id", person_id).execute()
            
            return person_id
        
        # Person doesn't exist — create new
        # Check slug collision
        slug_check = self.client.table("people").select("id").eq("id", slug).execute()
        
        if slug_check.data and len(slug_check.data) > 0:
            # Slug taken — append tmdb_id
            slug = f"{slug}-{tmdb_id}"
        
        # Insert new person
        profile_data["id"] = slug
        profile_data["tmdb_id"] = tmdb_id
        
        self.client.table("people").insert(profile_data).execute()
        self._cache[tmdb_id] = slug
        
        return slug
    
    def _upsert_by_slug(self, slug: str, profile_data: dict[str, Any]) -> str:
        """Upsert person by slug (for people without tmdb_id)."""
        profile_data["id"] = slug
        self.client.table("people").upsert(profile_data).execute()
        return slug
    
    def bulk_resolve(
        self,
        people_data: list[dict[str, Any]],
    ) -> dict[int, str]:
        """
        Batch resolve multiple people.
        
        Returns: {tmdb_id: person_id}
        """
        results: dict[int, str] = {}
        
        for data in people_data:
            tmdb_id = data.get("tmdb_id")
            if tmdb_id is None:
                continue
            
            person_id = self.resolve_or_create(
                tmdb_id=tmdb_id,
                name=data["name"],
                slug=data["id"],
                profile_data=data,
            )
            results[tmdb_id] = person_id
        
        return results
