try {
  // define toolbar buttons to show
  // if this value is undefined or its length is 0, default toolbar buttons will be shown
  const buttons = [
    'select',
    'shapes',
    'draw',
    'line',
    'path',
    'textbox',
    'upload',
    'background',
    'silhouetteColor',
    'silhouetteScale',
    'undo',
    'redo',
    'save',
    'download',
    'clear'
];


  // define custom shapes
  // if this value is undefined or its length is 0, default shapes will be used
  const shapes = [
    `<svg viewBox="-10 -10 180 180" fill="none" stroke="none" stroke-linecap="square" stroke-miterlimit="10"><path stroke="#000000" stroke-width="8" stroke-linecap="butt" d="m0 0l25.742783 0l0 0l38.614174 0l90.09974 0l0 52.74803l0 0l0 22.6063l0 15.070862l-90.09974 0l-61.5304 52.813744l22.916225 -52.813744l-25.742783 0l0 -15.070862l0 -22.6063l0 0z" fill-rule="evenodd"></path></svg>`,
    `<svg viewBox="-10 -10 180 180" fill="none" stroke="none" stroke-linecap="square" stroke-miterlimit="10"><path stroke="#000000" stroke-width="8" stroke-linejoin="round" stroke-linecap="butt" d="m1.0425826 140.35696l25.78009 -49.87359l0 0c-30.142242 -17.309525 -35.62507 -47.05113 -12.666686 -68.71045c22.958385 -21.65932 66.84442 -28.147947 101.387596 -14.990329c34.543175 13.1576185 48.438576 41.655407 32.10183 65.83693c-16.336761 24.181526 -57.559166 36.132935 -95.233955 27.61071z" fill-rule="evenodd"></path></svg>`,
    `<svg viewBox="0 -5 100 100" x="0px" y="0px"><path fill="none" stroke="#000" stroke-width="8" d="M55.2785222,56.3408313 C51.3476874,61.3645942 45.2375557,64.5921788 38.3756345,64.5921788 C31.4568191,64.5921788 25.3023114,61.3108505 21.3754218,56.215501 C10.6371566,55.0276798 2.28426396,45.8997866 2.28426396,34.8156425 C2.28426396,27.0769445 6.35589452,20.2918241 12.4682429,16.4967409 C14.7287467,7.0339786 23.2203008,0 33.3502538,0 C38.667844,0 43.5339584,1.93827732 47.284264,5.14868458 C51.0345695,1.93827732 55.9006839,0 61.2182741,0 C73.0769771,0 82.6903553,9.6396345 82.6903553,21.5307263 C82.6903553,22.0787821 82.6699341,22.6220553 82.629813,23.1598225 C87.1459866,27.1069477 90,32.9175923 90,39.396648 C90,51.2877398 80.3866218,60.9273743 68.5279188,60.9273743 C63.5283115,60.9273743 58.9277995,59.2139774 55.2785222,56.3408313 L55.2785222,56.3408313 Z M4.79695431,82 C7.44623903,82 9.59390863,80.6668591 9.59390863,79.0223464 C9.59390863,77.3778337 7.44623903,76.0446927 4.79695431,76.0446927 C2.1476696,76.0446927 0,77.3778337 0,79.0223464 C0,80.6668591 2.1476696,82 4.79695431,82 Z M13.7055838,71.9217877 C18.4995275,71.9217877 22.3857868,69.4606044 22.3857868,66.424581 C22.3857868,63.3885576 18.4995275,60.9273743 13.7055838,60.9273743 C8.91163999,60.9273743 5.02538071,63.3885576 5.02538071,66.424581 C5.02538071,69.4606044 8.91163999,71.9217877 13.7055838,71.9217877 Z"></path></svg>`
  ];

  var imgEditor = new ImageEditor('#image-editor-container', buttons, []);
  console.log('initialize image editor');

  window.addEventListener("message", function (event) {
    if (!event.data || !event.data.action) return;

    console.log("Mensagem recebida no editor:", event.data);

    if (event.data.action === "loadSilhouette" && event.data.url) {
        console.log("Carregando silhueta:", event.data.url);
        setTimeout(() => {
          carregarSilhueta(event.data.url);
      }, 500);  // Aguarda 500ms para garantir que o canvas está pronto
    }

    if (event.data.action === "loadGalleryImage" && event.data.url) {
        console.log("Carregando imagem da galeria:", event.data.url);
        carregarImagem(event.data.url);
    }
});

function carregarImagem(url) {
    const canvas = imgEditor.canvas;
    fabric.Image.fromURL(url, function (img) {
        img.set({
            left: canvas.width / 2,
            top: canvas.height / 2,
            originX: "center",
            originY: "center",
            selectable: true
        });
        canvas.add(img);
        canvas.renderAll();
    }, { crossOrigin: "anonymous" });
}

function carregarSilhueta(url) {
  const canvas = imgEditor.canvas;
  
  // Limpa o canvas antes de carregar a nova silhueta
  canvas.clear();
  
  // Desabilitar a seleção de objetos no canvas
  canvas.selection = false;
  
  fabric.loadSVGFromURL(url, function(objects, options) {
      const silhouette = fabric.util.groupSVGElements(objects, options);
      silhouette.set({
          left: canvas.width / 2,
          top: canvas.height / 2,
          originX: "center",
          originY: "center",
          selectable: false,
          evented: false,
          fill: "black",
          opacity: 1,
          lockMovementX: true,
          lockMovementY: true,
          lockRotation: true,
          lockScalingX: true,
          lockScalingY: true,
          hasControls: false,
          hasBorders: false,
          hasRotatingPoint: false,
          excludeFromExport: false,
          zIndex: 2
      });

      // Criar uma camada fosca que cubra toda a tela
      const overlay = new fabric.Rect({
          left: 0,
          top: 0,
          width: canvas.width,
          height: canvas.height,
          fill: "rgba(0, 0, 0, 0.5)",
          selectable: false,
          evented: false,
          lockMovementX: true,
          lockMovementY: true,
          lockRotation: true,
          lockScalingX: true,
          lockScalingY: true,
          hasControls: false,
          hasBorders: false,
          hasRotatingPoint: false,
          excludeFromExport: false,
          zIndex: 1,
          hoverCursor: 'default'
      });

      // Adicionar primeiro o fundo fosco
      canvas.add(overlay);
      
      // Adicionar a silhueta por cima
      canvas.add(silhouette);
      
      // Configurar a silhueta para criar o recorte
      silhouette.globalCompositeOperation = "destination-out";
      
      // Garantir que a silhueta fique sempre visível
      canvas.bringToFront(silhouette);
      
      // Desabilitar eventos do mouse no canvas
      canvas.on('mouse:down', function(e) {
          e.stopPropagation();
      });
      
      canvas.on('mouse:move', function(e) {
          e.stopPropagation();
      });
      
      canvas.on('mouse:up', function(e) {
          e.stopPropagation();
      });
      
      // Desabilitar a seleção de objetos
      canvas.on('selection:created', function(e) {
          e.target.set('selectable', false);
          canvas.discardActiveObject();
      });
      
      canvas.on('selection:updated', function(e) {
          e.target.set('selectable', false);
          canvas.discardActiveObject();
      });
      
      canvas.renderAll();
  });
}

// let status = imgEditor.getCanvasJSON();
// imgEditor.setCanvasStatus(status);

} catch (_) {
  const browserWarning = document.createElement('div')
  browserWarning.innerHTML = '<p style="line-height: 26px; margin-top: 100px; font-size: 16px; color: #555">Your browser is out of date!<br/>Please update to a modern browser, for example:<a href="https://www.google.com/chrome/" target="_blank">Chrome</a>!</p>';

  browserWarning.setAttribute(
    'style',
    'position: fixed; z-index: 1000; width: 100%; height: 100%; top: 0; left: 0; background-color: #f9f9f9; text-align: center; color: #555;'
  )

  // check for flex and grid support
  let divGrid = document.createElement('div')
  divGrid.style['display'] = 'grid'
  let supportsGrid = divGrid.style['display'] === 'grid'

  let divFlex = document.createElement('div')
  divFlex.style['display'] = 'flex'
  let supportsFlex = divFlex.style['display'] === 'flex'

  if (!supportsGrid || !supportsFlex) {
    document.body.appendChild(browserWarning)
  }
}
document.addEventListener("DOMContentLoaded", function () {
  if (typeof window.imgEditor !== "undefined" && !document.querySelector("#toolbar")) {
      imgEditor.initializeToolbar();
      initializeToolbarEvents(); // Garante que os eventos sejam ativados
  }
});
