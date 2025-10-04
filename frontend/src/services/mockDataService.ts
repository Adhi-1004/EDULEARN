/**
 * Mock data service for when backend is not available
 */

export const mockGamificationData = {
  xp: 0,
  level: 1,
  streak: 0,
  longest_streak: 0,
  badges: [],
  next_level_xp: 100,
  progress_to_next_level: 0
};



export const mockBadgesData = [
  {
    name: "First Steps",
    description: "Complete your first assessment",
    icon: "🎯",
    xp_reward: 50,
    category: "achievement",
    rarity: "common",
    earned_at: new Date().toISOString()
  }
];
