<script lang="ts">
  import '../app.css';
  let { children } = $props();
  const sections = [
    { id: 'introduction', title: 'Introduction', href: '/report' },
    { id: 'content-based', title: 'Content-based filtering', href: '/report' },
    { id: 'trends', title: 'Rating Trends', href: '/report' },
    { id: 'collaborative', title: 'Collaborative filtering', href: '/report' },
    { id: 'implementation', title: 'Implementation', href: '/report' },
    { id: 'conclusion', title: 'Conclusion', href: '/report' },
  ];
  
  function scrollToSection(id: string) {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  }
  </script>
  
  
<!-- +layout.svelte -->
<div class="min-h-screen bg-gray-50">
  <!-- Navbar that maintains space but is invisible until hover -->
  <aside class="fixed left-0 w-64 group opacity-0 hover:opacity-100 transition-opacity duration-300">
    <nav class="sticky top-0 h-screen flex items-center ml-10">
      <ul class="space-y-2 w-full">
        {#each sections as section}
          <li>
            <button
              on:click={() => scrollToSection(section.id)}
              class="w-full text-left px-4 py-2 rounded-lg hover:bg-gray-100 text-gray-700"
            >
            {section.title}
            </button>
          </li>
        {/each}
      </ul>
    </nav>
  </aside>
  <!-- Main content -->
  <div class="flex justify-center">
    <!-- Using larger max-width and adjusted breakpoints -->
      <main class="min-h-screen w-full">
       <slot></slot>
      </main>
  </div>
</div>