export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.1"
  }
  public: {
    Tables: {
      awards: {
        Row: {
          country: string | null
          id: string
          name: string
          organization: string
          scoring_points: number
          tier: string | null
          type: Database["public"]["Enums"]["award_type"] | null
          wikidata_id: string | null
        }
        Insert: {
          country?: string | null
          id: string
          name: string
          organization: string
          scoring_points?: number
          tier?: string | null
          type?: Database["public"]["Enums"]["award_type"] | null
          wikidata_id?: string | null
        }
        Update: {
          country?: string | null
          id?: string
          name?: string
          organization?: string
          scoring_points?: number
          tier?: string | null
          type?: Database["public"]["Enums"]["award_type"] | null
          wikidata_id?: string | null
        }
        Relationships: []
      }
      collection_works: {
        Row: {
          collection_id: string
          position: number | null
          work_id: string
        }
        Insert: {
          collection_id: string
          position?: number | null
          work_id: string
        }
        Update: {
          collection_id?: string
          position?: number | null
          work_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "collection_works_collection_id_fkey"
            columns: ["collection_id"]
            isOneToOne: false
            referencedRelation: "film_collections"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "collection_works_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "color_page_films"
            referencedColumns: ["work_id"]
          },
          {
            foreignKeyName: "collection_works_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "works"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "collection_works_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "works_with_color"
            referencedColumns: ["id"]
          },
        ]
      }
      color_assignments: {
        Row: {
          ai_confidence: number | null
          assigned_at: string | null
          authorship_score: number | null
          canon_tier: string | null
          color_iconico: Database["public"]["Enums"]["prisma_color_id"]
          color_rank: number | null
          colores_secundarios:
            | Database["public"]["Enums"]["prisma_color_id"][]
            | null
          cultural_weight: number | null
          doctrine_version: string | null
          editorial_override: Json | null
          grado_abstraccion: string | null
          mode: Database["public"]["Enums"]["color_mode"]
          numeric_score: number | null
          pipeline_version: string | null
          popularity_score: number | null
          reasoning: Json | null
          review_status: string
          ritmo_visual: string | null
          source: Database["public"]["Enums"]["assignment_source"]
          temperatura_emocional: string | null
          tier: Database["public"]["Enums"]["color_tier"] | null
          tier_rank: number | null
          updated_at: string | null
          work_id: string
        }
        Insert: {
          ai_confidence?: number | null
          assigned_at?: string | null
          authorship_score?: number | null
          canon_tier?: string | null
          color_iconico: Database["public"]["Enums"]["prisma_color_id"]
          color_rank?: number | null
          colores_secundarios?:
            | Database["public"]["Enums"]["prisma_color_id"][]
            | null
          cultural_weight?: number | null
          doctrine_version?: string | null
          editorial_override?: Json | null
          grado_abstraccion?: string | null
          mode: Database["public"]["Enums"]["color_mode"]
          numeric_score?: number | null
          pipeline_version?: string | null
          popularity_score?: number | null
          reasoning?: Json | null
          review_status?: string
          ritmo_visual?: string | null
          source?: Database["public"]["Enums"]["assignment_source"]
          temperatura_emocional?: string | null
          tier?: Database["public"]["Enums"]["color_tier"] | null
          tier_rank?: number | null
          updated_at?: string | null
          work_id: string
        }
        Update: {
          ai_confidence?: number | null
          assigned_at?: string | null
          authorship_score?: number | null
          canon_tier?: string | null
          color_iconico?: Database["public"]["Enums"]["prisma_color_id"]
          color_rank?: number | null
          colores_secundarios?:
            | Database["public"]["Enums"]["prisma_color_id"][]
            | null
          cultural_weight?: number | null
          doctrine_version?: string | null
          editorial_override?: Json | null
          grado_abstraccion?: string | null
          mode?: Database["public"]["Enums"]["color_mode"]
          numeric_score?: number | null
          pipeline_version?: string | null
          popularity_score?: number | null
          reasoning?: Json | null
          review_status?: string
          ritmo_visual?: string | null
          source?: Database["public"]["Enums"]["assignment_source"]
          temperatura_emocional?: string | null
          tier?: Database["public"]["Enums"]["color_tier"] | null
          tier_rank?: number | null
          updated_at?: string | null
          work_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "color_assignments_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: true
            referencedRelation: "color_page_films"
            referencedColumns: ["work_id"]
          },
          {
            foreignKeyName: "color_assignments_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: true
            referencedRelation: "works"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "color_assignments_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: true
            referencedRelation: "works_with_color"
            referencedColumns: ["id"]
          },
        ]
      }
      film_collections: {
        Row: {
          created_at: string | null
          description: string | null
          director_id: string | null
          id: string
          name: string
          tmdb_id: number | null
        }
        Insert: {
          created_at?: string | null
          description?: string | null
          director_id?: string | null
          id: string
          name: string
          tmdb_id?: number | null
        }
        Update: {
          created_at?: string | null
          description?: string | null
          director_id?: string | null
          id?: string
          name?: string
          tmdb_id?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "film_collections_director_id_fkey"
            columns: ["director_id"]
            isOneToOne: false
            referencedRelation: "people"
            referencedColumns: ["id"]
          },
        ]
      }
      film_submissions: {
        Row: {
          copyright_attested: boolean
          countries: string[] | null
          filmmaker_bio: string | null
          filmmaker_email: string
          filmmaker_name: string
          filmmaker_website: string | null
          genres: string[] | null
          id: number
          languages: string[] | null
          published_at: string | null
          rejection_reason: string | null
          reviewed_at: string | null
          reviewer_notes: string | null
          runtime_min: number | null
          status: Database["public"]["Enums"]["submission_status"]
          storage_path: string | null
          submitted_at: string | null
          submitter_user_id: string | null
          synopsis: string | null
          title: string
          work_id: string | null
          year: number | null
        }
        Insert: {
          copyright_attested?: boolean
          countries?: string[] | null
          filmmaker_bio?: string | null
          filmmaker_email: string
          filmmaker_name: string
          filmmaker_website?: string | null
          genres?: string[] | null
          id?: number
          languages?: string[] | null
          published_at?: string | null
          rejection_reason?: string | null
          reviewed_at?: string | null
          reviewer_notes?: string | null
          runtime_min?: number | null
          status?: Database["public"]["Enums"]["submission_status"]
          storage_path?: string | null
          submitted_at?: string | null
          submitter_user_id?: string | null
          synopsis?: string | null
          title: string
          work_id?: string | null
          year?: number | null
        }
        Update: {
          copyright_attested?: boolean
          countries?: string[] | null
          filmmaker_bio?: string | null
          filmmaker_email?: string
          filmmaker_name?: string
          filmmaker_website?: string | null
          genres?: string[] | null
          id?: number
          languages?: string[] | null
          published_at?: string | null
          rejection_reason?: string | null
          reviewed_at?: string | null
          reviewer_notes?: string | null
          runtime_min?: number | null
          status?: Database["public"]["Enums"]["submission_status"]
          storage_path?: string | null
          submitted_at?: string | null
          submitter_user_id?: string | null
          synopsis?: string | null
          title?: string
          work_id?: string | null
          year?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "film_submissions_submitter_user_id_fkey"
            columns: ["submitter_user_id"]
            isOneToOne: false
            referencedRelation: "user_profiles"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "film_submissions_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "color_page_films"
            referencedColumns: ["work_id"]
          },
          {
            foreignKeyName: "film_submissions_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "works"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "film_submissions_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "works_with_color"
            referencedColumns: ["id"]
          },
        ]
      }
      follows: {
        Row: {
          created_at: string | null
          follower_id: string
          following_id: string
        }
        Insert: {
          created_at?: string | null
          follower_id: string
          following_id: string
        }
        Update: {
          created_at?: string | null
          follower_id?: string
          following_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "follows_follower_id_fkey"
            columns: ["follower_id"]
            isOneToOne: false
            referencedRelation: "user_profiles"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "follows_following_id_fkey"
            columns: ["following_id"]
            isOneToOne: false
            referencedRelation: "user_profiles"
            referencedColumns: ["id"]
          },
        ]
      }
      generated_articles: {
        Row: {
          canonical_url: string | null
          content_md: string
          excerpt: string | null
          generated_at: string | null
          id: number
          is_published: boolean
          meta_description: string | null
          meta_title: string | null
          no_index: boolean
          published_at: string | null
          related_colors: string[] | null
          related_countries: string[] | null
          related_decades: string[] | null
          related_people: string[] | null
          related_works: string[] | null
          reviewed_at: string | null
          slug: string
          status: string | null
          template_type: string
          title: string
          updated_at: string | null
          word_count: number | null
        }
        Insert: {
          canonical_url?: string | null
          content_md: string
          excerpt?: string | null
          generated_at?: string | null
          id?: number
          is_published?: boolean
          meta_description?: string | null
          meta_title?: string | null
          no_index?: boolean
          published_at?: string | null
          related_colors?: string[] | null
          related_countries?: string[] | null
          related_decades?: string[] | null
          related_people?: string[] | null
          related_works?: string[] | null
          reviewed_at?: string | null
          slug: string
          status?: string | null
          template_type: string
          title: string
          updated_at?: string | null
          word_count?: number | null
        }
        Update: {
          canonical_url?: string | null
          content_md?: string
          excerpt?: string | null
          generated_at?: string | null
          id?: number
          is_published?: boolean
          meta_description?: string | null
          meta_title?: string | null
          no_index?: boolean
          published_at?: string | null
          related_colors?: string[] | null
          related_countries?: string[] | null
          related_decades?: string[] | null
          related_people?: string[] | null
          related_works?: string[] | null
          reviewed_at?: string | null
          slug?: string
          status?: string | null
          template_type?: string
          title?: string
          updated_at?: string | null
          word_count?: number | null
        }
        Relationships: []
      }
      news_items: {
        Row: {
          id: number
          ingested_at: string | null
          is_published: boolean
          published_at: string | null
          related_works: string[] | null
          source_name: string
          source_url: string
          summary: string | null
          title: string
        }
        Insert: {
          id?: number
          ingested_at?: string | null
          is_published?: boolean
          published_at?: string | null
          related_works?: string[] | null
          source_name: string
          source_url: string
          summary?: string | null
          title: string
        }
        Update: {
          id?: number
          ingested_at?: string | null
          is_published?: boolean
          published_at?: string | null
          related_works?: string[] | null
          source_name?: string
          source_url?: string
          summary?: string | null
          title?: string
        }
        Relationships: []
      }
      people: {
        Row: {
          bio: string | null
          birth_year: number | null
          death_year: number | null
          gender: number | null
          id: string
          name: string
          nationality: string[] | null
          profile_path: string | null
          search_vector: unknown
          tmdb_id: number | null
          updated_at: string | null
          wikidata_id: string | null
        }
        Insert: {
          bio?: string | null
          birth_year?: number | null
          death_year?: number | null
          gender?: number | null
          id: string
          name: string
          nationality?: string[] | null
          profile_path?: string | null
          search_vector?: unknown
          tmdb_id?: number | null
          updated_at?: string | null
          wikidata_id?: string | null
        }
        Update: {
          bio?: string | null
          birth_year?: number | null
          death_year?: number | null
          gender?: number | null
          id?: string
          name?: string
          nationality?: string[] | null
          profile_path?: string | null
          search_vector?: unknown
          tmdb_id?: number | null
          updated_at?: string | null
          wikidata_id?: string | null
        }
        Relationships: []
      }
      person_color_profiles: {
        Row: {
          color_distribution: Json
          dominant_color: Database["public"]["Enums"]["prisma_color_id"] | null
          film_count: number
          person_id: string
          role_context: Database["public"]["Enums"]["person_role"]
          updated_at: string | null
        }
        Insert: {
          color_distribution?: Json
          dominant_color?: Database["public"]["Enums"]["prisma_color_id"] | null
          film_count?: number
          person_id: string
          role_context?: Database["public"]["Enums"]["person_role"]
          updated_at?: string | null
        }
        Update: {
          color_distribution?: Json
          dominant_color?: Database["public"]["Enums"]["prisma_color_id"] | null
          film_count?: number
          person_id?: string
          role_context?: Database["public"]["Enums"]["person_role"]
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "person_color_profiles_person_id_fkey"
            columns: ["person_id"]
            isOneToOne: false
            referencedRelation: "people"
            referencedColumns: ["id"]
          },
        ]
      }
      ranking_scores: {
        Row: {
          context: string
          entity_id: string
          entity_type: string
          rank: number | null
          score: number
          updated_at: string | null
        }
        Insert: {
          context?: string
          entity_id: string
          entity_type: string
          rank?: number | null
          score: number
          updated_at?: string | null
        }
        Update: {
          context?: string
          entity_id?: string
          entity_type?: string
          rank?: number | null
          score?: number
          updated_at?: string | null
        }
        Relationships: []
      }
      review_likes: {
        Row: {
          created_at: string | null
          rating_id: number
          user_id: string
        }
        Insert: {
          created_at?: string | null
          rating_id: number
          user_id: string
        }
        Update: {
          created_at?: string | null
          rating_id?: number
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "review_likes_rating_id_fkey"
            columns: ["rating_id"]
            isOneToOne: false
            referencedRelation: "user_ratings"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "review_likes_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "user_profiles"
            referencedColumns: ["id"]
          },
        ]
      }
      studios: {
        Row: {
          country: string | null
          founded_year: number | null
          id: string
          logo_path: string | null
          name: string
          tmdb_id: number | null
          updated_at: string | null
          wikidata_id: string | null
        }
        Insert: {
          country?: string | null
          founded_year?: number | null
          id: string
          logo_path?: string | null
          name: string
          tmdb_id?: number | null
          updated_at?: string | null
          wikidata_id?: string | null
        }
        Update: {
          country?: string | null
          founded_year?: number | null
          id?: string
          logo_path?: string | null
          name?: string
          tmdb_id?: number | null
          updated_at?: string | null
          wikidata_id?: string | null
        }
        Relationships: []
      }
      user_profiles: {
        Row: {
          avatar_url: string | null
          bio: string | null
          created_at: string | null
          display_name: string | null
          id: string
          updated_at: string | null
          username: string
        }
        Insert: {
          avatar_url?: string | null
          bio?: string | null
          created_at?: string | null
          display_name?: string | null
          id: string
          updated_at?: string | null
          username: string
        }
        Update: {
          avatar_url?: string | null
          bio?: string | null
          created_at?: string | null
          display_name?: string | null
          id?: string
          updated_at?: string | null
          username?: string
        }
        Relationships: []
      }
      user_ratings: {
        Row: {
          created_at: string | null
          id: number
          is_public: boolean
          rating: number
          review: string | null
          updated_at: string | null
          user_id: string
          work_id: string
        }
        Insert: {
          created_at?: string | null
          id?: number
          is_public?: boolean
          rating: number
          review?: string | null
          updated_at?: string | null
          user_id: string
          work_id: string
        }
        Update: {
          created_at?: string | null
          id?: number
          is_public?: boolean
          rating?: number
          review?: string | null
          updated_at?: string | null
          user_id?: string
          work_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_ratings_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "user_profiles"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "user_ratings_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "color_page_films"
            referencedColumns: ["work_id"]
          },
          {
            foreignKeyName: "user_ratings_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "works"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "user_ratings_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "works_with_color"
            referencedColumns: ["id"]
          },
        ]
      }
      user_watches: {
        Row: {
          user_id: string
          work_id: string
          watched_at: string
          added_at: string | null
        }
        Insert: {
          user_id: string
          work_id: string
          watched_at?: string
          added_at?: string | null
        }
        Update: {
          user_id?: string
          work_id?: string
          watched_at?: string
          added_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "user_watches_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "user_profiles"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "user_watches_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "works"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "user_watches_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "works_with_color"
            referencedColumns: ["id"]
          },
        ]
      }
      user_watchlist: {
        Row: {
          user_id: string
          work_id: string
          added_at: string | null
        }
        Insert: {
          user_id: string
          work_id: string
          added_at?: string | null
        }
        Update: {
          user_id?: string
          work_id?: string
          added_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "user_watchlist_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "user_profiles"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "user_watchlist_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "works"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "user_watchlist_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "works_with_color"
            referencedColumns: ["id"]
          },
        ]
      }
      watchlists: {
        Row: {
          added_at: string | null
          note: string | null
          user_id: string
          work_id: string
        }
        Insert: {
          added_at?: string | null
          note?: string | null
          user_id: string
          work_id: string
        }
        Update: {
          added_at?: string | null
          note?: string | null
          user_id?: string
          work_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "watchlists_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "user_profiles"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "watchlists_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "color_page_films"
            referencedColumns: ["work_id"]
          },
          {
            foreignKeyName: "watchlists_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "works"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "watchlists_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "works_with_color"
            referencedColumns: ["id"]
          },
        ]
      }
      work_awards: {
        Row: {
          award_id: string
          category: string | null
          id: number
          person_id: string | null
          result: Database["public"]["Enums"]["award_result"]
          work_id: string
          year: number | null
        }
        Insert: {
          award_id: string
          category?: string | null
          id?: number
          person_id?: string | null
          result?: Database["public"]["Enums"]["award_result"]
          work_id: string
          year?: number | null
        }
        Update: {
          award_id?: string
          category?: string | null
          id?: number
          person_id?: string | null
          result?: Database["public"]["Enums"]["award_result"]
          work_id?: string
          year?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "work_awards_award_id_fkey"
            columns: ["award_id"]
            isOneToOne: false
            referencedRelation: "awards"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "work_awards_person_id_fkey"
            columns: ["person_id"]
            isOneToOne: false
            referencedRelation: "people"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "work_awards_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "color_page_films"
            referencedColumns: ["work_id"]
          },
          {
            foreignKeyName: "work_awards_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "works"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "work_awards_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "works_with_color"
            referencedColumns: ["id"]
          },
        ]
      }
      work_people: {
        Row: {
          billing_order: number | null
          person_id: string
          role: Database["public"]["Enums"]["person_role"]
          work_id: string
        }
        Insert: {
          billing_order?: number | null
          person_id: string
          role: Database["public"]["Enums"]["person_role"]
          work_id: string
        }
        Update: {
          billing_order?: number | null
          person_id?: string
          role?: Database["public"]["Enums"]["person_role"]
          work_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "work_people_person_id_fkey"
            columns: ["person_id"]
            isOneToOne: false
            referencedRelation: "people"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "work_people_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "color_page_films"
            referencedColumns: ["work_id"]
          },
          {
            foreignKeyName: "work_people_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "works"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "work_people_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "works_with_color"
            referencedColumns: ["id"]
          },
        ]
      }
      work_studios: {
        Row: {
          studio_id: string
          work_id: string
        }
        Insert: {
          studio_id: string
          work_id: string
        }
        Update: {
          studio_id?: string
          work_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "work_studios_studio_id_fkey"
            columns: ["studio_id"]
            isOneToOne: false
            referencedRelation: "studios"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "work_studios_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "color_page_films"
            referencedColumns: ["work_id"]
          },
          {
            foreignKeyName: "work_studios_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "works"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "work_studios_work_id_fkey"
            columns: ["work_id"]
            isOneToOne: false
            referencedRelation: "works_with_color"
            referencedColumns: ["id"]
          },
        ]
      }
      works: {
        Row: {
          arthouse_dist: string | null
          countries: string[]
          criterion_title: boolean
          duration_min: number | null
          genres: string[]
          id: string
          imdb_id: string | null
          imdb_rating: number | null
          imdb_votes: number | null
          ingested_at: string | null
          is_published: boolean
          is_sight_and_sound: boolean
          is_streamable: boolean
          languages: string[]
          mubi_title: boolean
          original_title: string | null
          search_vector: unknown
          streaming_id: string | null
          streaming_type:
            | Database["public"]["Enums"]["streaming_provider"]
            | null
          streaming_url: string | null
          synopsis: string | null
          tagline: string | null
          title: string
          tmdb_id: number | null
          tmdb_popularity: number | null
          tmdb_poster_path: string | null
          trailer_key: string | null
          type: Database["public"]["Enums"]["work_type"]
          updated_at: string | null
          where_to_watch: Json | null
          wikidata_id: string | null
          year: number | null
        }
        Insert: {
          arthouse_dist?: string | null
          countries?: string[]
          criterion_title?: boolean
          duration_min?: number | null
          genres?: string[]
          id: string
          imdb_id?: string | null
          imdb_rating?: number | null
          imdb_votes?: number | null
          ingested_at?: string | null
          is_published?: boolean
          is_sight_and_sound?: boolean
          is_streamable?: boolean
          languages?: string[]
          mubi_title?: boolean
          original_title?: string | null
          search_vector?: unknown
          streaming_id?: string | null
          streaming_type?:
            | Database["public"]["Enums"]["streaming_provider"]
            | null
          streaming_url?: string | null
          synopsis?: string | null
          tagline?: string | null
          title: string
          tmdb_id?: number | null
          tmdb_popularity?: number | null
          tmdb_poster_path?: string | null
          trailer_key?: string | null
          type: Database["public"]["Enums"]["work_type"]
          updated_at?: string | null
          where_to_watch?: Json | null
          wikidata_id?: string | null
          year?: number | null
        }
        Update: {
          arthouse_dist?: string | null
          countries?: string[]
          criterion_title?: boolean
          duration_min?: number | null
          genres?: string[]
          id?: string
          imdb_id?: string | null
          imdb_rating?: number | null
          imdb_votes?: number | null
          ingested_at?: string | null
          is_published?: boolean
          is_sight_and_sound?: boolean
          is_streamable?: boolean
          languages?: string[]
          mubi_title?: boolean
          original_title?: string | null
          search_vector?: unknown
          streaming_id?: string | null
          streaming_type?:
            | Database["public"]["Enums"]["streaming_provider"]
            | null
          streaming_url?: string | null
          synopsis?: string | null
          tagline?: string | null
          title?: string
          tmdb_id?: number | null
          tmdb_popularity?: number | null
          tmdb_poster_path?: string | null
          trailer_key?: string | null
          type?: Database["public"]["Enums"]["work_type"]
          updated_at?: string | null
          where_to_watch?: Json | null
          wikidata_id?: string | null
          year?: number | null
        }
        Relationships: []
      }
    }
    Views: {
      color_page_films: {
        Row: {
          color_iconico: Database["public"]["Enums"]["prisma_color_id"] | null
          colores_secundarios:
            | Database["public"]["Enums"]["prisma_color_id"][]
            | null
          countries: string[] | null
          criterion_title: boolean | null
          numeric_score: number | null
          tier: Database["public"]["Enums"]["color_tier"] | null
          tier_rank: number | null
          title: string | null
          tmdb_poster_path: string | null
          work_id: string | null
          year: number | null
        }
        Relationships: []
      }
      works_with_color: {
        Row: {
          color_iconico: Database["public"]["Enums"]["prisma_color_id"] | null
          color_mode: Database["public"]["Enums"]["color_mode"] | null
          colores_secundarios:
            | Database["public"]["Enums"]["prisma_color_id"][]
            | null
          countries: string[] | null
          criterion_title: boolean | null
          genres: string[] | null
          global_rank: number | null
          id: string | null
          is_published: boolean | null
          mubi_title: boolean | null
          numeric_score: number | null
          prestige_score: number | null
          tier: Database["public"]["Enums"]["color_tier"] | null
          tier_rank: number | null
          title: string | null
          tmdb_poster_path: string | null
          type: Database["public"]["Enums"]["work_type"] | null
          year: number | null
        }
        Relationships: []
      }
    }
    Functions: {
      get_arthouse_score: {
        Args: {
          arthouse_dist: string
          criterion_title: boolean
          mubi_title: boolean
        }
        Returns: number
      }
      get_canon_tier_multiplier: { Args: { tier: string }; Returns: number }
      refresh_work_rankings: { Args: never; Returns: undefined }
      show_limit: { Args: never; Returns: number }
      show_trgm: { Args: { "": string }; Returns: string[] }
    }
    Enums: {
      assignment_source: "ai" | "editorial" | "hybrid"
      award_result: "win" | "nomination"
      award_type: "festival" | "academy" | "guild" | "critics"
      color_mode: "color" | "monochromatic"
      color_tier: "canon" | "core" | "strong" | "peripheral" | "uncertain"
      person_role:
        | "director"
        | "cinematography"
        | "actor"
        | "writer"
        | "editor"
        | "composer"
        | "production_design"
      prisma_color_id:
        | "rojo_pasional"
        | "naranja_apocaliptico"
        | "ambar_desertico"
        | "amarillo_ludico"
        | "verde_lima"
        | "verde_esmeralda"
        | "verde_distopico"
        | "cian_melancolico"
        | "azul_nocturno"
        | "violeta_cinetico"
        | "purpura_onirico"
        | "magenta_pop"
        | "blanco_polar"
        | "negro_abismo"
        | "titanio_mecanico"
        | "claroscuro_dramatico"
        | "monocromatico_intimo"
      ranking_context:
        | "global"
        | "director"
        | "actor"
        | "dp"
        | "writer"
        | "country_ar"
        | "country_at"
        | "country_br"
        | "country_cn"
        | "country_de"
        | "country_dk"
        | "country_es"
        | "country_fr"
        | "country_gb"
        | "country_hu"
        | "country_in"
        | "country_ir"
        | "country_it"
        | "country_jp"
        | "country_kr"
        | "country_mx"
        | "country_ng"
        | "country_pl"
        | "country_pt"
        | "country_ro"
        | "country_ru"
        | "country_se"
        | "country_tw"
        | "country_us"
      streaming_provider: "bunny" | "mux" | "youtube_embed" | "vimeo"
      submission_status: "pending" | "under_review" | "approved" | "rejected"
      work_type: "film" | "short" | "series" | "music_video"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {
      assignment_source: ["ai", "editorial", "hybrid"],
      award_result: ["win", "nomination"],
      award_type: ["festival", "academy", "guild", "critics"],
      color_mode: ["color", "monochromatic"],
      color_tier: ["canon", "core", "strong", "peripheral", "uncertain"],
      person_role: [
        "director",
        "cinematography",
        "actor",
        "writer",
        "editor",
        "composer",
        "production_design",
      ],
      prisma_color_id: [
        "rojo_pasional",
        "naranja_apocaliptico",
        "ambar_desertico",
        "amarillo_ludico",
        "verde_lima",
        "verde_esmeralda",
        "verde_distopico",
        "cian_melancolico",
        "azul_nocturno",
        "violeta_cinetico",
        "purpura_onirico",
        "magenta_pop",
        "blanco_polar",
        "negro_abismo",
        "titanio_mecanico",
        "claroscuro_dramatico",
        "monocromatico_intimo",
      ],
      ranking_context: [
        "global",
        "director",
        "actor",
        "dp",
        "writer",
        "country_ar",
        "country_at",
        "country_br",
        "country_cn",
        "country_de",
        "country_dk",
        "country_es",
        "country_fr",
        "country_gb",
        "country_hu",
        "country_in",
        "country_ir",
        "country_it",
        "country_jp",
        "country_kr",
        "country_mx",
        "country_ng",
        "country_pl",
        "country_pt",
        "country_ro",
        "country_ru",
        "country_se",
        "country_tw",
        "country_us",
      ],
      streaming_provider: ["bunny", "mux", "youtube_embed", "vimeo"],
      submission_status: ["pending", "under_review", "approved", "rejected"],
      work_type: ["film", "short", "series", "music_video"],
    },
  },
} as const
