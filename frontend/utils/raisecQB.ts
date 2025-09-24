import { Question } from '@/types/journey'


export const mockQuestionsWithMetadata: Question[] = [
  {
    question_id: "q-001",
    question_number: 1,
    question_text: "Work Environment Preference\nWhich type of work environment would you most enjoy?",
    options: [
      {
        id: "A",
        text: "Working with tools and machinery in a workshop",
        riasec_weights: { realistic: 0.9, investigative: 0.2, artistic: 0.1, social: 0.1, enterprising: 0.1, conventional: 0.1 },
        motivators: [],
        interests: [],
        confidence_impact: 7.5
      },
      {
        id: "B",
        text: "Conducting research in a laboratory",
        riasec_weights: { realistic: 0.2, investigative: 0.9, artistic: 0.1, social: 0.1, enterprising: 0.1, conventional: 0.2 },
        motivators: [],
        interests: [],
        confidence_impact: 7.8
      },
      {
        id: "C",
        text: "Creating artwork in a studio",
        riasec_weights: { realistic: 0.1, investigative: 0.1, artistic: 0.9, social: 0.2, enterprising: 0.2, conventional: 0.1 },
        motivators: [],
        interests: [],
        confidence_impact: 7.2
      },
      {
        id: "D",
        text: "Teaching and helping people in a classroom",
        riasec_weights: { realistic: 0.1, investigative: 0.2, artistic: 0.2, social: 0.9, enterprising: 0.2, conventional: 0.2 },
        motivators: [],
        interests: [],
        confidence_impact: 7.6
      }
    ],
    target_dimensions: { primary: "riasec", secondary: [] },
    context_note: "Work environment preference mapped to RIASEC"
  },
  {
    question_id: "q-002",
    question_number: 2,
    question_text: "Career Activity Interest\nWhich activity sounds most appealing to you?",
    options: [
      {
        id: "A",
        text: "Leading a business presentation to potential clients",
        riasec_weights: { realistic: 0.1, investigative: 0.2, artistic: 0.1, social: 0.3, enterprising: 0.9, conventional: 0.2 },
        motivators: [],
        interests: [],
        confidence_impact: 7.9
      },
      {
        id: "B",
        text: "Organizing and managing company financial records",
        riasec_weights: { realistic: 0.1, investigative: 0.2, artistic: 0.1, social: 0.1, enterprising: 0.3, conventional: 0.9 },
        motivators: [],
        interests: [],
        confidence_impact: 7.4
      },
      {
        id: "C",
        text: "Building and repairing electronic devices",
        riasec_weights: { realistic: 0.9, investigative: 0.3, artistic: 0.1, social: 0.1, enterprising: 0.2, conventional: 0.1 },
        motivators: [],
        interests: [],
        confidence_impact: 7.6
      },
      {
        id: "D",
        text: "Analyzing scientific data to solve complex problems",
        riasec_weights: { realistic: 0.2, investigative: 0.9, artistic: 0.1, social: 0.1, enterprising: 0.2, conventional: 0.2 },
        motivators: [],
        interests: [],
        confidence_impact: 8.0
      }
    ],
    target_dimensions: { primary: "riasec", secondary: [] },
    context_note: "Activity preference mapped to RIASEC"
  },
  {
    question_id: "q-003",
    question_number: 3,
    question_text: "Personal Work Style\nHow do you prefer to approach your work?",
    options: [
      {
        id: "A",
        text: "Following clear procedures and maintaining detailed records",
        riasec_weights: { realistic: 0.1, investigative: 0.2, artistic: 0.1, social: 0.2, enterprising: 0.2, conventional: 0.9 },
        motivators: [],
        interests: [],
        confidence_impact: 7.3
      },
      {
        id: "B",
        text: "Using creativity and imagination to develop new ideas",
        riasec_weights: { realistic: 0.1, investigative: 0.2, artistic: 0.9, social: 0.3, enterprising: 0.3, conventional: 0.1 },
        motivators: [],
        interests: [],
        confidence_impact: 7.7
      },
      {
        id: "C",
        text: "Working with people to help solve their problems",
        riasec_weights: { realistic: 0.2, investigative: 0.2, artistic: 0.3, social: 0.9, enterprising: 0.3, conventional: 0.2 },
        motivators: [],
        interests: [],
        confidence_impact: 7.8
      },
      {
        id: "D",
        text: "Taking charge and persuading others to follow your vision",
        riasec_weights: { realistic: 0.2, investigative: 0.2, artistic: 0.2, social: 0.3, enterprising: 0.9, conventional: 0.3 },
        motivators: [],
        interests: [],
        confidence_impact: 8.1
      }
    ],
    target_dimensions: { primary: "riasec", secondary: [] },
    context_note: "Work style preference mapped to RIASEC"
  },
  {
    question_id: "q-004",
    question_number: 4,
    question_text: "Task Preference\nWhich task would you find most satisfying?",
    options: [
      {
        id: "A",
        text: "Performing scientific experiments and research",
        riasec_weights: { realistic: 0.2, investigative: 0.9, artistic: 0.2, social: 0.2, enterprising: 0.2, conventional: 0.2 },
        motivators: [],
        interests: [],
        confidence_impact: 8.0
      },
      {
        id: "B",
        text: "Working outdoors with your hands on practical projects",
        riasec_weights: { realistic: 0.9, investigative: 0.3, artistic: 0.1, social: 0.2, enterprising: 0.2, conventional: 0.2 },
        motivators: [],
        interests: [],
        confidence_impact: 7.5
      },
      {
        id: "C",
        text: "Writing creative stories or designing visual content",
        riasec_weights: { realistic: 0.1, investigative: 0.2, artistic: 0.9, social: 0.3, enterprising: 0.3, conventional: 0.1 },
        motivators: [],
        interests: [],
        confidence_impact: 7.4
      },
      {
        id: "D",
        text: "Managing budgets and organizing office systems",
        riasec_weights: { realistic: 0.1, investigative: 0.2, artistic: 0.1, social: 0.2, enterprising: 0.2, conventional: 0.9 },
        motivators: [],
        interests: [],
        confidence_impact: 7.2
      }
    ],
    target_dimensions: { primary: "riasec", secondary: [] },
    context_note: "Task satisfaction preference mapped to RIASEC"
  },
  {
    question_id: "q-005",
    question_number: 5,
    question_text: "Career Goal\nWhat type of career goal appeals to you most?",
    options: [
      {
        id: "A",
        text: "Becoming a counselor who helps people with personal issues",
        riasec_weights: { realistic: 0.1, investigative: 0.2, artistic: 0.2, social: 0.9, enterprising: 0.2, conventional: 0.2 },
        motivators: [],
        interests: [],
        confidence_impact: 7.9
      },
      {
        id: "B",
        text: "Starting your own successful business venture",
        riasec_weights: { realistic: 0.2, investigative: 0.3, artistic: 0.2, social: 0.3, enterprising: 0.9, conventional: 0.2 },
        motivators: [],
        interests: [],
        confidence_impact: 8.2
      },
      {
        id: "C",
        text: "Working as a mechanic fixing cars and machinery",
        riasec_weights: { realistic: 0.9, investigative: 0.3, artistic: 0.1, social: 0.1, enterprising: 0.2, conventional: 0.2 },
        motivators: [],
        interests: [],
        confidence_impact: 7.6
      },
      {
        id: "D",
        text: "Becoming a scientist who discovers new medical treatments",
        riasec_weights: { realistic: 0.2, investigative: 0.9, artistic: 0.2, social: 0.2, enterprising: 0.2, conventional: 0.2 },
        motivators: [],
        interests: [],
        confidence_impact: 8.3
      }
    ],
    target_dimensions: { primary: "riasec", secondary: [] },
    context_note: "Career goal identification mapped to RIASEC"
  },
  {
    question_id: "q-006",
    question_number: 6,
    question_text: "Daily Activity Interest\nWhich daily activity would you most enjoy?",
    options: [
      {
        id: "A",
        text: "Playing musical instruments or acting in plays",
        riasec_weights: { realistic: 0.1, investigative: 0.1, artistic: 0.9, social: 0.3, enterprising: 0.2, conventional: 0.1 },
        motivators: [],
        interests: [],
        confidence_impact: 7.4
      },
      {
        id: "B",
        text: "Managing files, typing, and organizing data",
        riasec_weights: { realistic: 0.1, investigative: 0.2, artistic: 0.1, social: 0.1, enterprising: 0.2, conventional: 0.9 },
        motivators: [],
        interests: [],
        confidence_impact: 7.0
      },
      {
        id: "C",
        text: "Teaching or training others in new skills",
        riasec_weights: { realistic: 0.1, investigative: 0.2, artistic: 0.2, social: 0.9, enterprising: 0.3, conventional: 0.2 },
        motivators: [],
        interests: [],
        confidence_impact: 7.8
      },
      {
        id: "D",
        text: "Giving speeches and leading group discussions",
        riasec_weights: { realistic: 0.2, investigative: 0.2, artistic: 0.2, social: 0.3, enterprising: 0.9, conventional: 0.3 },
        motivators: [],
        interests: [],
        confidence_impact: 8.1
      }
    ],
    target_dimensions: { primary: "riasec", secondary: [] },
    context_note: "Daily activity preference mapped to RIASEC"
  }
]
