<script lang="ts">
import { onMount, onDestroy } from 'svelte';
import { writable, type Writable } from 'svelte/store';
import { Editor, rootCtx, defaultValueCtx } from '@milkdown/kit/core';
import { commonmark } from '@milkdown/kit/preset/commonmark';
import { nord } from '@milkdown/theme-nord';
import { katexOptionsCtx, math } from '@milkdown/plugin-math';
import { listener, listenerCtx } from '@milkdown/plugin-listener';
import type { Editor as MilkdownEditor } from '@milkdown/core';

interface SaveStatus {
    saving: boolean;
    lastSaved: string | null;
    error: string | null;
}

interface Section {
    name: string;
    content: string;
    lastModified: string;
}

export let sectionName = 'default';
let editorRef: HTMLDivElement;
let editorInstance: MilkdownEditor | null = null;
let isEditable = true;
let sections: Section[] = [];

const editorContent: Writable<string> = writable('');
const saveStatus: Writable<SaveStatus> = writable({ 
    saving: false, 
    lastSaved: null,
    error: null 
});

async function loadSections() {
  console.log('try calling server !');
    const response = await fetch('/save/api/report/sections');
    const data = await response.json();
    sections = data.sections;
    isEditable = data.editable;
}

async function loadContent() {
    const response = await fetch(`/save/api/report/content?section=${sectionName}`);
    const data = await response.json();
    isEditable = data.editable;
    return data.content;
}

async function saveContent(content: string): Promise<void> {
    if (!isEditable) return;

    try {
        saveStatus.set({ saving: true, lastSaved: null, error: null });
        
        const response = await fetch('/save/api/report/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ content, section: sectionName }),
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || 'Failed to save content');
        }

        saveStatus.set({ 
            saving: false, 
            lastSaved: new Date().toISOString(),
            error: null 
        });
    } catch (error) {
        console.error('Error saving content:', error);
        saveStatus.set({ 
            saving: false, 
            lastSaved: null,
            error: error instanceof Error ? error.message : 'Failed to save changes'
        });
    }
}

const debouncedSave = debounce(saveContent, 1000);

onMount(async () => {
    try {
        await loadSections();
        const content = await loadContent();
        if (editorRef) {
            editorInstance = await createEditor(editorRef, content);
            
            editorContent.subscribe((content) => {
                if (content && isEditable) {
                    debouncedSave(content);
                }
            });
        }
    } catch (error) {
        console.error('Error initializing editor:', error);
        saveStatus.set({
            saving: false,
            lastSaved: null,
            error: 'Failed to initialize editor'
        });
    }
});

onDestroy(() => {
    if (editorInstance) {
        editorInstance.destroy();
    }
});
    
    function createEditor(dom: HTMLDivElement, initialContent: string = ''): Promise<MilkdownEditor> {
      return Editor.make()
      .use(commonmark)
      .use(math)
        .use(listener)
        .config((ctx) => {
          ctx.set(katexOptionsCtx.key, {         throwOnError: false, // Don't throw on parsing errors
            errorColor: '#BF616A', // Nord red color
            strict: false, // Be less strict about syntax
            trust: true // Allow more commands
          });
          ctx.set(rootCtx, dom);
          ctx.set(defaultValueCtx, initialContent);
          ctx.get(listenerCtx).markdownUpdated((_, markdown, prevMarkdown) => {
          if (markdown !== prevMarkdown) {
            editorContent.set(markdown);
          }
        });
      })
        .create();
    }
    
    // Debounce function to limit save requests
    function debounce<T extends (...args: any[]) => any>(
      func: T, 
      wait: number
    ): (...args: Parameters<T>) => void {
      let timeout: number;
      return (...args: Parameters<T>): void => {
        const later = () => {
          clearTimeout(timeout);
          func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
      };
    }
    
</script>
    
    <div class="editor-container ">
      <div class="editor" bind:this={editorRef}></div>
      
      {#if $saveStatus.saving}
        <div class="status saving">
          Saving changes...
        </div>
      {:else if $saveStatus.error}
        <div class="status error">
          {$saveStatus.error}
        </div>
      {:else if $saveStatus.lastSaved}
        <div class="status saved">
          Last saved at {new Date($saveStatus.lastSaved).toLocaleTimeString()}
        </div>
      {/if}
    </div>
    
    <style>
      .editor-container {
        @apply relative rounded-lg bg-white;
      }
    
      .editor {
        @apply w-auto;
      }
    
      .status {
        @apply absolute bottom-2 right-2 text-sm px-2 py-1 rounded;
      }
    
      .saving {
        @apply bg-blue-100 text-blue-700;
      }
    
      .error {
        @apply bg-red-100 text-red-700;
      }
    
      .saved {
        @apply bg-green-100 text-green-700;
      }

  /* Target the ProseMirror editor content */
  :global(.editor-container .ProseMirror) {
    word-wrap: break-word;
    overflow-wrap: break-word;
    white-space: pre-wrap;
  }

  /* If you have code blocks that need special handling */
  :global(.editor-container pre) {
    white-space: pre-wrap;
    overflow-x: auto;
    max-width: 100%;
  }

  /* For inline code */
  :global(.editor-container code) {
    word-break: break-all;
    white-space: pre-wrap;
  }
  /* Remove the blue outline on focus */
  :global(.ProseMirror) {
    outline: none !important;
  }
    </style>