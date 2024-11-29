<!-- routes/report/+layout.svelte -->
<script lang="ts">
    const sections = [
      { id: 'overview', title: 'Overview', href: '/report#overview' },
      { id: 'ratings', title: 'Ratings Analysis', href: '/report#ratings' },
      { id: 'trends', title: 'Rating Trends', href: '/report#trends' },
      { id: 'recommendations', title: 'Recommendations', href: '/report#recommendations' }
    ];

    function scrollToSection(id: string) {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  }

  
  </script>
  
  <div class="flex min-h-screen bg-gray-50">
    <aside class="w-64 bg-white border-r border-gray-200">
      <nav class="p-4 sticky top-0">
        <h2 class="text-xl font-bold mb-4">Report Sections</h2>
        <ul class="space-y-2">
          {#each sections as section}
          <li>
            <button
              on:click={() => scrollToSection(section.id)}
              class="w-full text-left px-4 py-2 rounded-lg hover:bg-gray-50 text-gray-700"
            >
              {section.title}
            </button>
          </li>
          {/each}
        </ul>
      </nav>
    </aside>
  
    <main class="flex-1 p-8">
      <slot />
    </main>
  </div>