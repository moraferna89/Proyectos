export const SITE_CONFIG = {
  name: "Clínica Veterinaria Huellas",
  shortName: "Huellas",
  tagline: "El bienestar de tu mascota, nuestra misión",
  description:
    "Clínica veterinaria de confianza en Concepción. Tu veterinario de cabecera para que tu mascota crezca fuerte y sana.",
  address: "Paicaví 976 Local 3, Concepción",
  addressDetail: "Entre calle Los Carreras y Bulnes",
  phone: "(41) 2733332",
  phoneHref: "tel:+56412733332",
  email: "contacto@veterinariahuellas.cl",
  instagram: "https://www.instagram.com/veterinariahuellas/",
  mapEmbed:
    "https://maps.google.com/maps?q=Paicaví+976+Local+3,+Concepción,+Chile&t=&z=17&ie=UTF8&iwloc=&output=embed",
  mapLink:
    "https://www.google.com/maps/search/Paicaví+976+Local+3,+Concepción,+Chile",
};

export const SCHEDULE = [
  { day: "Lunes a Viernes", hours: "10:30 – 18:30" },
  { day: "Sábados", hours: "Cerrado" },
  { day: "Domingos y Festivos", hours: "Cerrado" },
];

export const SERVICES = [
  {
    id: "consulta",
    title: "Consulta Veterinaria",
    description:
      "Atención personalizada con diagnóstico integral para mantener a tu mascota en óptimas condiciones de salud.",
    icon: "Stethoscope",
    gradient: "from-blue-500 to-sky-500",
    lightBg: "bg-blue-50",
    iconColor: "text-blue-600",
  },
  {
    id: "cirugia",
    title: "Cirugía",
    description:
      "Procedimientos quirúrgicos especializados: esterilización, otoplastia y atención de urgencias quirúrgicas.",
    icon: "Activity",
    gradient: "from-blue-500 to-blue-700",
    lightBg: "bg-blue-50",
    iconColor: "text-blue-600",
  },
  {
    id: "farmacia",
    title: "Farmacia Veterinaria",
    description:
      "Amplio stock de medicamentos, antiparasitarios y productos de salud para todas las especies.",
    icon: "Pill",
    gradient: "from-purple-500 to-purple-700",
    lightBg: "bg-purple-50",
    iconColor: "text-purple-600",
  },
  {
    id: "peluqueria",
    title: "Peluquería Canina",
    description:
      "Servicio de grooming profesional: baño, corte y estética para que tu perro luzca y se sienta increíble.",
    icon: "Scissors",
    gradient: "from-pink-500 to-rose-600",
    lightBg: "bg-pink-50",
    iconColor: "text-pink-600",
  },
  {
    id: "alimentacion",
    title: "Alimentación",
    description:
      "Alimentos premium balanceados para perros y gatos en todas las etapas de vida y necesidades especiales.",
    icon: "ShoppingBag",
    gradient: "from-amber-500 to-orange-600",
    lightBg: "bg-amber-50",
    iconColor: "text-amber-600",
  },
  {
    id: "accesorios",
    title: "Accesorios",
    description:
      "Todo lo que tu mascota necesita: correas, camas, juguetes, collares y mucho más en un solo lugar.",
    icon: "Package",
    gradient: "from-teal-500 to-cyan-600",
    lightBg: "bg-teal-50",
    iconColor: "text-teal-600",
  },
  {
    id: "limpieza-dental",
    title: "Limpieza Dental",
    description:
      "Profilaxis dental profesional para prevenir enfermedades periodontales y mantener una sonrisa sana.",
    icon: "Smile",
    gradient: "from-indigo-500 to-indigo-700",
    lightBg: "bg-indigo-50",
    iconColor: "text-indigo-600",
  },
];

export const STATS = [
  { value: 15, suffix: "+", label: "Años de experiencia", icon: "Award" },
  {
    value: 5000,
    suffix: "+",
    label: "Mascotas atendidas",
    icon: "Heart",
  },
  { value: 7, suffix: "", label: "Servicios especializados", icon: "Star" },
  { value: 98, suffix: "%", label: "Clientes satisfechos", icon: "ThumbsUp" },
];

export const FAQ_ITEMS = [
  {
    question: "¿Con qué frecuencia debo llevar a mi mascota al veterinario?",
    answer:
      "Se recomienda una revisión anual para mascotas adultas sanas. Los cachorros y gatitos necesitan visitas más frecuentes durante el primer año para completar su plan de vacunación. Las mascotas senior (mayores de 7 años) deberían visitarse al menos dos veces al año.",
  },
  {
    question: "¿Qué vacunas necesita mi perro o gato?",
    answer:
      "Para perros, las vacunas esenciales incluyen la Polivalente (moquillo, parvovirus, hepatitis) y la antirrábica. Para gatos, la trivalente felina y la antirrábica. Te guiamos con un plan de vacunación personalizado según la edad y estilo de vida de tu mascota.",
  },
  {
    question: "¿A qué edad se recomienda esterilizar a mi mascota?",
    answer:
      "En general, se recomienda entre los 6 y 12 meses de edad, antes del primer celo en hembras. Sin embargo, la edad ideal puede variar según la raza y el tamaño. Nuestros veterinarios te orientarán con una recomendación personalizada.",
  },
  {
    question: "¿Cómo puedo saber si mi mascota está enferma?",
    answer:
      "Señales de alerta incluyen: pérdida de apetito o sed excesiva, letargo o cambios de comportamiento, vómitos o diarrea persistentes, dificultad para respirar, cojera o dolor al moverse, y cambios en heces u orina. Ante cualquier síntoma preocupante, consúltanos.",
  },
  {
    question: "¿Atienden urgencias?",
    answer:
      "Atendemos urgencias dentro de nuestro horario de atención (Lunes a Viernes, 10:30 a 18:30). Para emergencias fuera de ese horario, te recomendamos dirigirte a una clínica veterinaria de urgencia 24 horas en Concepción.",
  },
  {
    question: "¿Cuál es el horario de atención?",
    answer:
      "Atendemos de Lunes a Viernes de 10:30 a 18:30 horas. Los sábados, domingos y festivos permanecemos cerrados. Te recomendamos agendar tu hora con anticipación para asegurar tu atención.",
  },
  {
    question: "¿Tienen estacionamiento disponible?",
    answer:
      "Sí, contamos con amplio estacionamiento disponible para nuestros clientes. Nos encontramos en Paicaví 976 Local 3, Concepción, entre las calles Los Carreras y Bulnes.",
  },
  {
    question: "¿Cómo puedo agendar una consulta?",
    answer:
      "Puedes agendar tu hora llamando al (41) 2733332, enviando un correo a contacto@veterinariahuellas.cl, o completando el formulario de contacto en este sitio. ¡También puedes visitarnos directamente en nuestra clínica!",
  },
];

export const BLOG_POSTS = [
  {
    id: 1,
    title: "Guía completa de vacunación para perros y gatos",
    excerpt:
      "Las vacunas son esenciales para proteger a tu mascota de enfermedades graves. Conoce el calendario de vacunación recomendado por nuestros especialistas.",
    date: "15 Mayo, 2024",
    category: "Salud Preventiva",
    image:
      "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=800&h=500&fit=crop&q=80",
    slug: "guia-vacunacion-perros-gatos",
    readTime: "5 min",
  },
  {
    id: 2,
    title: "¿Cómo elegir el mejor alimento para tu mascota?",
    excerpt:
      "La nutrición es la base de la salud de tu compañero. Te ayudamos a entender las etiquetas y elegir el alimento ideal según edad, raza y condición.",
    date: "2 Abril, 2024",
    category: "Nutrición",
    image:
      "https://images.unsplash.com/photo-1601758124510-52d02ddb7cbd?w=800&h=500&fit=crop&q=80",
    slug: "elegir-mejor-alimento-mascota",
    readTime: "4 min",
  },
  {
    id: 3,
    title: "Señales de alerta: ¿Cuándo ir al veterinario de urgencia?",
    excerpt:
      "Aprende a identificar los síntomas que requieren atención veterinaria inmediata. Actuar a tiempo puede salvar la vida de tu mascota.",
    date: "20 Marzo, 2024",
    category: "Cuidados",
    image:
      "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=800&h=500&fit=crop&q=80",
    slug: "senales-alerta-veterinario-urgencia",
    readTime: "6 min",
  },
];

export const GALLERY_IMAGES = [
  {
    id: 1,
    src: "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=500&h=500&fit=crop&q=80",
    alt: "Golden Retriever feliz",
    name: "Max",
  },
  {
    id: 2,
    src: "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=500&h=500&fit=crop&q=80",
    alt: "Gato en revisión",
    name: "Luna",
  },
  {
    id: 3,
    src: "https://images.unsplash.com/photo-1552053831-71594a27632d?w=500&h=500&fit=crop&q=80",
    alt: "Perrito curioso",
    name: "Simón",
  },
  {
    id: 4,
    src: "https://images.unsplash.com/photo-1548802673-380ab8a66f96?w=500&h=500&fit=crop&q=80",
    alt: "Cachorro en atención",
    name: "Coco",
  },
  {
    id: 5,
    src: "https://images.unsplash.com/photo-1561037404-61cd46aa615b?w=500&h=500&fit=crop&q=80",
    alt: "Dos perros amigos",
    name: "Bruno y Lola",
  },
  {
    id: 6,
    src: "https://images.unsplash.com/photo-1526336024174-e58f5cdd8e13?w=500&h=500&fit=crop&q=80",
    alt: "Gatito descansando",
    name: "Michi",
  },
];

export const NAV_LINKS = [
  { label: "Inicio", href: "#inicio" },
  { label: "Servicios", href: "#servicios" },
  { label: "Nosotros", href: "#nosotros" },
  { label: "Pacientes", href: "#pacientes" },
  { label: "FAQ", href: "#faq" },
  { label: "Blog", href: "#blog" },
  { label: "Contacto", href: "#contacto" },
];

export const PET_TYPES = [
  "Perro",
  "Gato",
  "Ave",
  "Conejo",
  "Reptil",
  "Otro",
];
