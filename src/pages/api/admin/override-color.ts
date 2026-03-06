// filepath: src/pages/api/admin/override-color.ts
import type { APIRoute } from 'astro';
import { createServiceClient } from '../../../lib/db/client';
import { PRISMA_PALETTE } from '../../../lib/color/colorPalette';

export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json();
    const { work_id, color_iconico, colores_secundarios, editorial_note } = body;

    // Validation
    if (!work_id || typeof work_id !== 'string') {
      return new Response(JSON.stringify({ error: 'Missing or invalid work_id' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    if (!color_iconico || typeof color_iconico !== 'string') {
      return new Response(JSON.stringify({ error: 'Missing or invalid color_iconico' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Validate color_iconico exists in palette
    if (!PRISMA_PALETTE[color_iconico]) {
      return new Response(JSON.stringify({ error: `Invalid color ID: ${color_iconico}` }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Validate secondary colors (max 2)
    let secondaryColors: string[] = [];
    if (Array.isArray(colores_secundarios)) {
      if (colores_secundarios.length > 2) {
        return new Response(JSON.stringify({ error: 'Maximum 2 secondary colors allowed' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        });
      }
      
      // Validate each secondary color exists in palette
      for (const colorId of colores_secundarios) {
        if (!PRISMA_PALETTE[colorId]) {
          return new Response(JSON.stringify({ error: `Invalid secondary color ID: ${colorId}` }), {
            status: 400,
            headers: { 'Content-Type': 'application/json' }
          });
        }
      }
      
      secondaryColors = colores_secundarios;
    }

    // Create editorial override object
    const editorialOverride: any = {
      overridden_at: new Date().toISOString(),
      overridden_by: 'curator', // TODO: Add actual user authentication
      note: editorial_note || '',
      original_color: null as string | null, // Will be set by database trigger or application logic
    };

    // Update database
    const db = createServiceClient();
    
    // First, get the current assignment to preserve the original color
    const { data: currentAssignment, error: fetchError } = await db
      .from('color_assignments')
      .select('color_iconico, editorial_override')
      .eq('work_id', work_id)
      .single();

    if (fetchError) {
      console.error('[override-color] Error fetching current assignment:', fetchError);
      return new Response(JSON.stringify({ error: 'Failed to fetch current assignment' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Preserve original color if this is the first override
    if (!currentAssignment.editorial_override) {
      editorialOverride.original_color = currentAssignment.color_iconico;
    } else {
      // Keep the original from the first override
      const override = currentAssignment.editorial_override as any;
      editorialOverride.original_color = override.original_color;
    }

    // Update the assignment
    const { data, error } = await db
      .from('color_assignments')
      .update({
        color_iconico: color_iconico as any,
        colores_secundarios: secondaryColors as any,
        editorial_override: editorialOverride,
        review_status: 'approved', // Auto-approve curator overrides
        updated_at: new Date().toISOString()
      } as any)
      .eq('work_id', work_id)
      .select()
      .single();

    if (error) {
      console.error('[override-color] Database error:', error);
      return new Response(JSON.stringify({ error: 'Failed to save override' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Return success with updated color info
    const colorEntry = PRISMA_PALETTE[color_iconico];
    return new Response(JSON.stringify({
      success: true,
      work_id,
      color_iconico,
      color_hex: colorEntry.hex,
      color_name: colorEntry.name,
      colores_secundarios: secondaryColors,
      updated_at: data.updated_at
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (err) {
    console.error('[override-color] Unexpected error:', err);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
