<script>
  import { Editor, rootCtx, defaultValueCtx } from '@milkdown/kit/core';
  import { commonmark } from '@milkdown/kit/preset/commonmark';
  import { nord } from '@milkdown/theme-nord';
  
  function editor(dom) {
    // to obtain the editor instance we need to store a reference of the editor.
    const MakeEditor = Editor.make()
      .config((ctx) => {
        ctx.set(rootCtx, dom);
      })
      .config(nord)
      .use(commonmark)
      .create();
    MakeEditor.then((editor) => {
      // here you have access to the editor instance.
  
      // const exampleContent = "# Hello World!";
      // editor.action(replaceAll(exampleContent));
    })
  }
  </script>
  
  <div use:editor />