export const SITE_CONFIG = {
  name: "Fuente Divka",
  tagline: "Bar Cervecero",
  description:
    "18 variedades de cerveza artesanal, gastronomía gourmet y el mejor ambiente de Santiago. 12 años siendo la picada favorita de Apoquindo.",
  address: "Apoquindo 7645, Las Condes, Santiago",
  phone: "(2) 2974 2722",
  instagram: "https://www.instagram.com/fuente.divka/",
  tiktok: "https://www.tiktok.com/@fuentedivka",
  email: "contacto@fuentedivka.cl",
  hours: {
    weekdays: "Lun – Jue: 13:00 – 01:00",
    friday: "Vie: 13:00 – 03:00",
    weekend: "Sáb – Dom: 12:00 – 03:00",
  },
  coordinates: {
    lat: -33.4099,
    lng: -70.5747,
  },
};

export const NAV_LINKS = [
  { label: "Inicio", href: "#hero" },
  { label: "Nosotros", href: "#nosotros" },
  { label: "Cervezas", href: "#cervezas" },
  { label: "Carta", href: "#carta" },
  { label: "Ambiente", href: "#ambiente" },
  { label: "Contacto", href: "#contacto" },
];

export const BEERS = [
  {
    name: "Divka Rubia",
    style: "Lager Artesanal",
    abv: "4.8%",
    description: "Suave, refrescante y dorada. El clásico perfecto para empezar la noche.",
    ibu: 15,
    color: "Dorado",
    icon: "🍺",
  },
  {
    name: "Divka Roja",
    style: "Amber Ale",
    abv: "5.2%",
    description: "Caramelo, tostado y malta. Un equilibrio perfecto entre dulzura y amargor.",
    ibu: 22,
    color: "Ámbar",
    icon: "🍺",
  },
  {
    name: "Divka Negra",
    style: "Stout",
    abv: "6.0%",
    description: "Café, chocolate oscuro y cremosidad. Para los amantes de lo intenso.",
    ibu: 35,
    color: "Negro",
    icon: "🍺",
  },
  {
    name: "Divka IPA",
    style: "India Pale Ale",
    abv: "6.5%",
    description: "Cítricos, pino y lúpulo explosivo. La favorita de los hopheads.",
    ibu: 60,
    color: "Cobre",
    icon: "🍺",
  },
  {
    name: "Divka Trigo",
    style: "Wheat Beer",
    abv: "4.5%",
    description: "Ligera, afrutada y con notas de banana. Perfecta para días de sol.",
    ibu: 12,
    color: "Pálido",
    icon: "🍺",
  },
  {
    name: "Divka Porter",
    style: "Brown Porter",
    abv: "5.5%",
    description: "Vainilla, nuez y tostado suave. Profunda pero accesible.",
    ibu: 28,
    color: "Marrón",
    icon: "🍺",
  },
  {
    name: "Divka Pale",
    style: "American Pale Ale",
    abv: "5.0%",
    description: "Equilibrio perfecto entre maltas y lúpulos. Versátil y deliciosa.",
    ibu: 38,
    color: "Dorado",
    icon: "🍺",
  },
  {
    name: "Divka Sour",
    style: "Gose Sour",
    abv: "4.2%",
    description: "Ácida, frutal y refrescante. Para quienes buscan algo distinto.",
    ibu: 10,
    color: "Turbia",
    icon: "🍺",
  },
];

export const FOOD_ITEMS = [
  {
    category: "Tablas & Picadas",
    items: [
      {
        name: "Tabla Divka Completa",
        description: "Selección de fiambres premium, quesos artesanales, encurtidos y pan de campo.",
        price: "$18.900",
        badge: "Favorita",
      },
      {
        name: "Tabla de Quesos",
        description: "5 variedades de quesos nacionales e importados con frutos secos y miel.",
        price: "$14.500",
        badge: null,
      },
      {
        name: "Tabla Charcutería",
        description: "Jamón serrano, salame, pastrami y cecina con tostadas artesanales.",
        price: "$15.900",
        badge: null,
      },
    ],
  },
  {
    category: "Para Picar",
    items: [
      {
        name: "Papas Bravas Divka",
        description: "Papas rústicas con salsa brava especiada y aioli de ajo negro.",
        price: "$7.900",
        badge: "Nuevo",
      },
      {
        name: "Alitas BBQ Cerveceras",
        description: "Alitas glaseadas con reducción de cerveza negra y miel.",
        price: "$11.900",
        badge: null,
      },
      {
        name: "Nachos de la Casa",
        description: "Con guacamole, pico de gallo, crema agria y jalapeños frescos.",
        price: "$9.500",
        badge: null,
      },
    ],
  },
  {
    category: "Platos de Fondo",
    items: [
      {
        name: "Burger Fuente",
        description: "200g de carne premium, cheddar ahumado, cebolla caramelizada en cerveza.",
        price: "$13.900",
        badge: "Chef's Pick",
      },
      {
        name: "Hot Dog Gourmet",
        description: "Salchicha alemana, sauerkraut, mostaza Dijon y cebolla frita.",
        price: "$9.900",
        badge: null,
      },
    ],
  },
];

export const STATS = [
  { value: "12+", label: "Años de Historia" },
  { value: "18", label: "Cervezas Artesanales" },
  { value: "5K+", label: "Clientes Felices" },
  { value: "1", label: "Lugar Único" },
];

export const TESTIMONIALS = [
  {
    name: "Cristóbal M.",
    text: "La mejor cervecería de Apoquindo sin duda. Las cervezas artesanales son increíbles y el ambiente es único.",
    rating: 5,
  },
  {
    name: "Valentina R.",
    text: "Fuimos en grupo y quedamos encantados. Las tablas son generosas y la atención es excelente.",
    rating: 5,
  },
  {
    name: "Matías P.",
    text: "Lugar auténtico, con personalidad propia. Se nota el amor por la cerveza artesanal en cada detalle.",
    rating: 5,
  },
];
