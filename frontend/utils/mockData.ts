import { Question, OptionTarget } from '@/types/journey'

export const mockQuestionWithMetadata: Question = {
  question_id: "mock-001",
  question_number: 1,
  question_text: "You're at a career crossroads after 3 years in tech. Which path excites you most?",
  options: [
    {
      id: "A",
      text: "Joining a startup developing green technology solutions, working hands-on to build sustainable products that contribute to environmental conservation.",
      riasec_weights: {
        realistic: 0.7,
        investigative: 0.3,
        artistic: 0.1,
        social: 0.2,
        enterprising: 0.6,
        conventional: 0.1
      },
      motivators: [
        { type: "purpose", weight: 0.9 },
        { type: "autonomy", weight: 0.7 },
        { type: "challenge", weight: 0.6 }
      ],
      interests: [
        { area: "sustainability", weight: 0.9 },
        { area: "technology", weight: 0.7 }
      ],
      confidence_impact: 7.5
    },
    {
      id: "B",
      text: "Working as a data analyst for a leading e-commerce company, diving deep into consumer data to uncover insights that drive business decisions.",
      riasec_weights: {
        realistic: 0.1,
        investigative: 0.9,
        artistic: 0.1,
        social: 0.1,
        enterprising: 0.3,
        conventional: 0.4
      },
      motivators: [
        { type: "growth", weight: 0.8 },
        { type: "recognition", weight: 0.6 },
        { type: "stability", weight: 0.7 }
      ],
      interests: [
        { area: "analytics", weight: 0.9 },
        { area: "business", weight: 0.6 }
      ],
      confidence_impact: 8.0
    },
    {
      id: "C",
      text: "Becoming a creative content strategist at a dynamic advertising agency, crafting engaging narratives across digital platforms for various brands.",
      riasec_weights: {
        realistic: 0.1,
        investigative: 0.2,
        artistic: 0.9,
        social: 0.4,
        enterprising: 0.5,
        conventional: 0.1
      },
      motivators: [
        { type: "creativity", weight: 0.9 },
        { type: "autonomy", weight: 0.8 },
        { type: "team", weight: 0.6 }
      ],
      interests: [
        { area: "marketing", weight: 0.8 },
        { area: "storytelling", weight: 0.9 }
      ],
      confidence_impact: 7.0
    },
    {
      id: "D",
      text: "Taking up a role as community health coordinator with an NGO, improving healthcare accessibility through collaborative efforts.",
      riasec_weights: {
        realistic: 0.2,
        investigative: 0.2,
        artistic: 0.1,
        social: 0.9,
        enterprising: 0.3,
        conventional: 0.3
      },
      motivators: [
        { type: "purpose", weight: 0.9 },
        { type: "team", weight: 0.8 },
        { type: "work-life-balance", weight: 0.7 }
      ],
      interests: [
        { area: "healthcare", weight: 0.8 },
        { area: "community", weight: 0.9 }
      ],
      confidence_impact: 6.5
    }
  ],
  target_dimensions: {
    primary: "multi-dimensional",
    secondary: ["riasec", "motivators", "interests"]
  },
  context_note: "Career pivot exploration for mid-20s professional"
}