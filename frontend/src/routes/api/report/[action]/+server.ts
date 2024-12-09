// routes/api/report/[action]/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import fs from 'fs';
import path from 'path';

// Configuration
const REPORTS_DIR = 'data/reports';
const VERSIONS_DIR = 'versions';
const SECTIONS_DIR = 'sections';
const IS_PROD = process.env.NODE_ENV === 'production';
const EDITABLE = process.env.ALLOW_EDIT === 'true' || !IS_PROD;

interface ReportSection {
    name: string;
    content: string;
    lastModified: string;
}

// Ensure directory structure exists
function initializeDirectories() {
    const dirs = [
        REPORTS_DIR,
        path.join(REPORTS_DIR, VERSIONS_DIR),
        path.join(REPORTS_DIR, SECTIONS_DIR)
    ];

    dirs.forEach(dir => {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
    });
}

// Initialize directories on startup
initializeDirectories();

// Save a version of the content
function saveVersion(sectionName: string, content: string) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const versionPath = path.join(
        REPORTS_DIR, 
        VERSIONS_DIR, 
        `${sectionName}_${timestamp}.md`
    );
    fs.writeFileSync(versionPath, content, 'utf-8');
}

function sanitizeContent(content: string): string {
    return content
}

// Get all available sections
export const GET: RequestHandler = async ({ params, url }) => {
    if (!['content', 'sections'].includes(params.action)) {
        return json({ error: 'Invalid action' }, { status: 400 });
    }

    try {
        if (params.action === 'sections') {
            const sectionsPath = path.join(REPORTS_DIR, SECTIONS_DIR);
            const files = fs.readdirSync(sectionsPath);
            const sections: ReportSection[] = files
                .filter(file => file.endsWith('.md'))
                .map(file => {
                    const filePath = path.join(sectionsPath, file);
                    const content = fs.readFileSync(filePath, 'utf-8');
                    const stats = fs.statSync(filePath);
                    return {
                        name: file.replace('.md', ''),
                        content: sanitizeContent(content),
                        lastModified: stats.mtime.toISOString()
                    };
                });
            return json({ sections, editable: EDITABLE });
        }

        // Handle single section content
        const sectionName = url.searchParams.get('section');
        if (!sectionName) {
            return json({ error: 'Section name required' }, { status: 400 });
        }

        const sectionPath = path.join(REPORTS_DIR, SECTIONS_DIR, `${sectionName}.md`);
        if (!fs.existsSync(sectionPath)) {
            return json({ content: '', editable: EDITABLE });
        }

        const content = fs.readFileSync(sectionPath, 'utf-8');
        return json({ 
            content: sanitizeContent(content), 
            editable: EDITABLE 
        });
    } catch (error) {
        console.error('Error reading report:', error);
        return json({ error: 'Failed to read report' }, { status: 500 });
    }
};

export const POST: RequestHandler = async ({ params, request }) => {
    if (!EDITABLE) {
        return json({ error: 'Editing is disabled in production' }, { status: 403 });
    }

    if (params.action !== 'save') {
        return json({ error: 'Invalid action' }, { status: 400 });
    }

    try {
        const { content, section } = await request.json();
        
        if (typeof content !== 'string' || typeof section !== 'string') {
            return json({ error: 'Invalid content format' }, { status: 400 });
        }

        // Sanitize the content
        const sanitizedContent = sanitizeContent(content);

        // Save the current version
        saveVersion(section, sanitizedContent);

        // Save the new content
        const sectionPath = path.join(REPORTS_DIR, SECTIONS_DIR, `${section}.md`);
        fs.writeFileSync(sectionPath, sanitizedContent, 'utf-8');
        
        return json({ 
            success: true,
            message: 'Report saved successfully'
        });
    } catch (error) {
        console.error('Error saving report:', error);
        return json({ 
            success: false,
            error: 'Failed to save report'
        }, { status: 500 });
    }
};