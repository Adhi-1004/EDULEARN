# 👨‍🎓 Student Learning Platform Features

## Table of Contents
1. [Overview](#overview)
2. [Student Dashboard](#student-dashboard)
3. [Gamification System](#gamification-system)
4. [Assessment Taking](#assessment-taking)
5. [Results & Progress Tracking](#results--progress-tracking)
6. [Notifications](#notifications)
7. [Learning Analytics](#learning-analytics)

---

## Overview

The Student Learning Platform provides an engaging, gamified learning experience with comprehensive assessment tools and progress tracking.

### Key Features
- 📊 **Personalized Dashboard** - Progress overview and statistics
- 🎮 **Gamification** - XP, levels, badges, and streaks
- 📝 **Assessment Access** - Take MCQ and coding assessments
- 📈 **Progress Tracking** - Detailed performance analytics
- 🔔 **Notifications** - Real-time updates on assessments and achievements
- 🏆 **Leaderboards** - Compare performance with peers

---

## Student Dashboard

### Feature Overview
Centralized hub displaying learning progress, upcoming assessments, achievements, and key metrics.

### Dashboard Components

#### 1. Overview Cards
```typescript
// File: frontend/src/pages/student/Dashboard.tsx
const StudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [gamification, setGamification] = useState(null);
  
  useEffect(() => {
    loadDashboardData();
  }, []);
  
  const loadDashboardData = async () => {
    const [statsData, gamData] = await Promise.all([
      userService.getUserStats(user.id),
      userService.getGamification(user.id)
    ]);
    
    setStats(statsData);
    setGamification(gamData);
  };
  
  return (
    <div className="student-dashboard">
      <div className="welcome-section">
        <h1>Welcome back, {user.name}!</h1>
        <p>Level {gamification?.level} • {gamification?.xp} XP</p>
      </div>
      
      <div className="dashboard-grid">
        <StatsCard
          title="Assessments Completed"
          value={stats?.assessments_completed}
          icon={<AssessmentIcon />}
          color="blue"
        />
        
        <StatsCard
          title="Average Score"
          value={`${stats?.average_score?.toFixed(1)}%`}
          icon={<ScoreIcon />}
          color="green"
        />
        
        <StatsCard
          title="Current Streak"
          value={`${gamification?.streak} days`}
          icon={<FireIcon />}
          color="orange"
        />
        
        <StatsCard
          title="Badges Earned"
          value={gamification?.badges?.length}
          icon={<BadgeIcon />}
          color="purple"
        />
      </div>
      
      <div className="dashboard-content">
        <UpcomingAssessments />
        <RecentActivity />
        <Achievements badges={gamification?.badges} />
      </div>
    </div>
  );
};
```

#### Backend Dashboard Endpoint
```python
# File: backend/app/api/users.py
@router.get("/me/stats")
async def get_user_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get current user's statistics"""
    db = await get_db()
    user_id = current_user["_id"]
    
    # Get assessment submissions
    submissions = await db.assessment_submissions.find({
        "student_id": user_id
    }).to_list(length=None)
    
    # Calculate statistics
    total_assessments = len(submissions)
    avg_score = sum(s["percentage"] for s in submissions) / total_assessments if submissions else 0
    
    # Get coding solutions
    coding_solutions = await db.coding_solutions.count_documents({
        "user_id": ObjectId(user_id),
        "status": "accepted"
    })
    
    return {
        "assessments_completed": total_assessments,
        "average_score": avg_score,
        "problems_solved": coding_solutions,
        "total_xp": current_user.get("xp", 0)
    }
```

---

## Gamification System

### Feature Overview
Engaging reward system with XP, levels, badges, and streak tracking to motivate continuous learning.

### Gamification Components

#### 1. XP and Levels

```python
# File: backend/app/services/gamification.py
def calculate_level(xp: int) -> int:
    """Calculate level based on XP"""
    # Level formula: level = floor(sqrt(xp / 100))
    return int((xp / 100) ** 0.5) + 1

def xp_for_next_level(current_level: int) -> int:
    """Calculate XP needed for next level"""
    return (current_level ** 2) * 100

async def award_xp(db, user_id: str, xp_amount: int, reason: str):
    """Award XP to user and check for level up"""
    # Get current user stats
    user = await db.users.find_one({"_id": user_id})
    current_xp = user.get("xp", 0)
    current_level = user.get("level", 1)
    
    # Add XP
    new_xp = current_xp + xp_amount
    new_level = calculate_level(new_xp)
    
    # Update user
    await db.users.update_one(
        {"_id": user_id},
        {
            "$set": {"xp": new_xp, "level": new_level},
            "$push": {
                "xp_history": {
                    "amount": xp_amount,
                    "reason": reason,
                    "timestamp": datetime.utcnow()
                }
            }
        }
    )
    
    # Check for level up
    if new_level > current_level:
        await create_notification(
            db,
            user_id,
            "Level Up!",
            f"Congratulations! You've reached Level {new_level}!",
            "achievement"
        )
        
        # Award level up badge
        await award_badge(db, user_id, f"level_{new_level}")
    
    return {
        "xp_awarded": xp_amount,
        "total_xp": new_xp,
        "level": new_level,
        "leveled_up": new_level > current_level
    }
```

#### 2. Badge System

```python
# Badge definitions
BADGES = {
    "first_assessment": {
        "name": "Getting Started",
        "description": "Complete your first assessment",
        "icon": "🎯",
        "xp_bonus": 50
    },
    "perfect_score": {
        "name": "Perfectionist",
        "description": "Score 100% on an assessment",
        "icon": "💯",
        "xp_bonus": 100
    },
    "streak_7": {
        "name": "Week Warrior",
        "description": "Maintain a 7-day streak",
        "icon": "🔥",
        "xp_bonus": 200
    },
    "coding_master": {
        "name": "Coding Master",
        "description": "Solve 50 coding problems",
        "icon": "💻",
        "xp_bonus": 500
    }
}

async def check_and_award_badges(db, user_id: str):
    """Check and award eligible badges"""
    user = await db.users.find_one({"_id": user_id})
    earned_badges = user.get("badges", [])
    
    # Check first assessment badge
    if "first_assessment" not in earned_badges:
        submissions = await db.assessment_submissions.count_documents({
            "student_id": user_id
        })
        if submissions >= 1:
            await award_badge(db, user_id, "first_assessment")
    
    # Check perfect score badge
    if "perfect_score" not in earned_badges:
        perfect_scores = await db.assessment_submissions.count_documents({
            "student_id": user_id,
            "percentage": 100
        })
        if perfect_scores >= 1:
            await award_badge(db, user_id, "perfect_score")
    
    # Check coding master badge
    if "coding_master" not in earned_badges:
        solved = await db.coding_solutions.count_documents({
            "user_id": ObjectId(user_id),
            "status": "accepted"
        })
        if solved >= 50:
            await award_badge(db, user_id, "coding_master")

async def award_badge(db, user_id: str, badge_id: str):
    """Award a badge to user"""
    badge = BADGES[badge_id]
    
    await db.users.update_one(
        {"_id": user_id},
        {
            "$push": {
                "badges": {
                    "id": badge_id,
                    "name": badge["name"],
                    "description": badge["description"],
                    "icon": badge["icon"],
                    "earned_at": datetime.utcnow()
                }
            }
        }
    )
    
    # Award XP bonus
    await award_xp(db, user_id, badge["xp_bonus"], f"Badge: {badge['name']}")
    
    # Create notification
    await create_notification(
        db,
        user_id,
        "New Badge Earned!",
        f"{badge['icon']} {badge['name']}: {badge['description']}",
        "achievement"
    )
```

#### 3. Streak Tracking

```python
async def update_activity_streak(db, user_id: str):
    """Update user's activity streak"""
    user = await db.users.find_one({"_id": user_id})
    
    last_activity = user.get("last_activity_date")
    current_streak = user.get("streak", 0)
    today = datetime.utcnow().date()
    
    if last_activity:
        last_activity_date = last_activity.date()
        days_diff = (today - last_activity_date).days
        
        if days_diff == 0:
            # Same day, no change
            pass
        elif days_diff == 1:
            # Consecutive day, increment streak
            current_streak += 1
        else:
            # Streak broken
            current_streak = 1
    else:
        # First activity
        current_streak = 1
    
    # Update user
    await db.users.update_one(
        {"_id": user_id},
        {
            "$set": {
                "last_activity_date": datetime.utcnow(),
                "streak": current_streak,
                "longest_streak": max(current_streak, user.get("longest_streak", 0))
            }
        }
    )
    
    # Check for streak badges
    if current_streak == 7 and "streak_7" not in user.get("badges", []):
        await award_badge(db, user_id, "streak_7")
    
    return current_streak
```

#### Frontend Gamification Display

```typescript
// File: frontend/src/components/GamificationPanel.tsx
const GamificationPanel: React.FC = () => {
  const [gamData, setGamData] = useState(null);
  
  const progressToNextLevel = () => {
    const currentLevelXP = (gamData.level - 1) ** 2 * 100;
    const nextLevelXP = gamData.level ** 2 * 100;
    const progress = ((gamData.xp - currentLevelXP) / (nextLevelXP - currentLevelXP)) * 100;
    return Math.min(progress, 100);
  };
  
  return (
    <div className="gamification-panel">
      <div className="level-section">
        <h3>Level {gamData?.level}</h3>
        <div className="xp-bar">
          <div
            className="xp-progress"
            style={{ width: `${progressToNextLevel()}%` }}
          />
        </div>
        <p>{gamData?.xp} XP / {gamData?.level ** 2 * 100} XP</p>
      </div>
      
      <div className="streak-section">
        <div className="streak-icon">🔥</div>
        <div>
          <h4>{gamData?.streak} Day Streak</h4>
          <p>Keep it going!</p>
        </div>
      </div>
      
      <div className="badges-section">
        <h3>Badges ({gamData?.badges?.length})</h3>
        <div className="badges-grid">
          {gamData?.badges?.map((badge) => (
            <div key={badge.id} className="badge" title={badge.description}>
              <span className="badge-icon">{badge.icon}</span>
              <span className="badge-name">{badge.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
```

---

## Assessment Taking

(Covered in detail in [ASSESSMENT_FEATURES.md](./ASSESSMENT_FEATURES.md#student-assessment-taking))

### Quick Overview
- View available assessments assigned to student's batch
- Timed assessment interface with countdown timer
- Multiple-choice questions with single selection
- Auto-submit on timer expiration
- Immediate result feedback

---

## Results & Progress Tracking

### View Results

```python
# File: backend/app/api/results.py
@router.get("/user/{user_id}")
async def get_user_results(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all results for a user"""
    # Verify authorization
    if current_user["_id"] != user_id and current_user["role"] not in ["teacher", "admin"]:
        raise HTTPException(403, "Unauthorized")
    
    db = await get_db()
    
    # Get assessment submissions
    submissions = await db.assessment_submissions.find({
        "student_id": user_id
    }).sort("submitted_at", -1).to_list(length=None)
    
    # Get coding solutions
    coding_solutions = await db.coding_solutions.find({
        "user_id": ObjectId(user_id)
    }).sort("submitted_at", -1).to_list(length=None)
    
    # Enrich with assessment details
    for submission in submissions:
        assessment = await db.assessments.find_one({
            "_id": ObjectId(submission["assessment_id"])
        })
        submission["assessment_title"] = assessment["title"] if assessment else "Unknown"
    
    # Enrich with problem details
    for solution in coding_solutions:
        problem = await db.coding_problems.find_one({
            "_id": solution["problem_id"]
        })
        solution["problem_title"] = problem["title"] if problem else "Unknown"
    
    return {
        "assessment_results": submissions,
        "coding_solutions": coding_solutions,
        "total_assessments": len(submissions),
        "total_coding_problems": len(coding_solutions)
    }
```

### Progress Visualization

```typescript
// File: frontend/src/pages/student/Progress.tsx
import { Line, Bar } from 'react-chartjs-2';

const ProgressPage: React.FC = () => {
  const [results, setResults] = useState([]);
  
  const scoreData = {
    labels: results.map(r => new Date(r.submitted_at).toLocaleDateString()),
    datasets: [{
      label: 'Assessment Scores',
      data: results.map(r => r.percentage),
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1
    }]
  };
  
  const topicData = {
    labels: Object.keys(topicPerformance),
    datasets: [{
      label: 'Performance by Topic',
      data: Object.values(topicPerformance),
      backgroundColor: 'rgba(54, 162, 235, 0.5)'
    }]
  };
  
  return (
    <div className="progress-page">
      <h1>Your Progress</h1>
      
      <div className="charts">
        <div className="chart-container">
          <h3>Score Trend</h3>
          <Line data={scoreData} />
        </div>
        
        <div className="chart-container">
          <h3>Topic Performance</h3>
          <Bar data={topicData} />
        </div>
      </div>
      
      <div className="results-list">
        <h3>Recent Results</h3>
        {results.map(result => (
          <ResultCard key={result.id} result={result} />
        ))}
      </div>
    </div>
  );
};
```

---

## Notifications

### Feature Overview
Real-time notifications for assessments, achievements, and important updates.

```python
# File: backend/app/api/notifications.py
@router.get("/")
async def get_notifications(
    current_user: dict = Depends(get_current_user)
):
    """Get all notifications for current user"""
    db = await get_db()
    
    notifications = await db.notifications.find({
        "user_id": current_user["_id"]
    }).sort("created_at", -1).limit(50).to_list(length=None)
    
    return notifications

@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark notification as read"""
    db = await get_db()
    
    await db.notifications.update_one(
        {
            "_id": notification_id,
            "user_id": current_user["_id"]
        },
        {"$set": {"read": True}}
    )
    
    return {"message": "Notification marked as read"}

@router.get("/unread-count")
async def get_unread_count(
    current_user: dict = Depends(get_current_user)
):
    """Get count of unread notifications"""
    db = await get_db()
    
    count = await db.notifications.count_documents({
        "user_id": current_user["_id"],
        "read": False
    })
    
    return {"unread_count": count}
```

### Frontend Notifications

```typescript
// File: frontend/src/components/NotificationBell.tsx
const NotificationBell: React.FC = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showDropdown, setShowDropdown] = useState(false);
  
  useEffect(() => {
    loadNotifications();
    
    // Poll for new notifications every 30 seconds
    const interval = setInterval(loadNotifications, 30000);
    return () => clearInterval(interval);
  }, []);
  
  const loadNotifications = async () => {
    const [notifs, count] = await Promise.all([
      notificationService.getNotifications(),
      notificationService.getUnreadCount()
    ]);
    
    setNotifications(notifs);
    setUnreadCount(count.unread_count);
  };
  
  const handleMarkAsRead = async (notificationId: string) => {
    await notificationService.markAsRead(notificationId);
    loadNotifications();
  };
  
  return (
    <div className="notification-bell">
      <button onClick={() => setShowDropdown(!showDropdown)}>
        <BellIcon />
        {unreadCount > 0 && (
          <span className="badge">{unreadCount}</span>
        )}
      </button>
      
      {showDropdown && (
        <div className="notification-dropdown">
          <h3>Notifications</h3>
          {notifications.length === 0 ? (
            <p>No notifications</p>
          ) : (
            notifications.map(notif => (
              <div
                key={notif._id}
                className={`notification-item ${notif.read ? '' : 'unread'}`}
                onClick={() => handleMarkAsRead(notif._id)}
              >
                <h4>{notif.title}</h4>
                <p>{notif.message}</p>
                <span className="time">
                  {new Date(notif.created_at).toLocaleString()}
                </span>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
```

---

## Learning Analytics

### Personal Analytics Dashboard

```python
@router.get("/{user_id}/analytics")
async def get_user_analytics(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive learning analytics"""
    db = await get_db()
    
    # Assessment analytics
    submissions = await db.assessment_submissions.find({
        "student_id": user_id
    }).to_list(length=None)
    
    # Time-based performance
    monthly_performance = {}
    for submission in submissions:
        month_key = submission["submitted_at"].strftime("%Y-%m")
        if month_key not in monthly_performance:
            monthly_performance[month_key] = {"total": 0, "avg_score": 0}
        monthly_performance[month_key]["total"] += 1
        monthly_performance[month_key]["avg_score"] += submission["percentage"]
    
    # Calculate averages
    for month in monthly_performance:
        total = monthly_performance[month]["total"]
        monthly_performance[month]["avg_score"] /= total
    
    # Subject-wise performance
    subject_performance = {}
    for submission in submissions:
        assessment = await db.assessments.find_one({
            "_id": ObjectId(submission["assessment_id"])
        })
        if assessment:
            subject = assessment["subject"]
            if subject not in subject_performance:
                subject_performance[subject] = []
            subject_performance[subject].append(submission["percentage"])
    
    # Calculate subject averages
    for subject in subject_performance:
        scores = subject_performance[subject]
        subject_performance[subject] = {
            "average": sum(scores) / len(scores),
            "count": len(scores),
            "best": max(scores),
            "latest": scores[-1]
        }
    
    return {
        "monthly_performance": monthly_performance,
        "subject_performance": subject_performance,
        "total_assessments": len(submissions),
        "overall_average": sum(s["percentage"] for s in submissions) / len(submissions) if submissions else 0
    }
```

---

## Summary

### Student Features Matrix

| Feature | Key Files | Main Endpoints |
|---------|-----------|----------------|
| Dashboard | `Dashboard.tsx`, `users.py` | `GET /users/me`, `GET /users/me/stats` |
| Gamification | `GamificationPanel.tsx`, `gamification.py` | `GET /users/{id}/gamification` |
| Assessments | `TakeAssessment.tsx`, `submissions.py` | `GET /assessments/student/available` |
| Results | `Results.tsx`, `results.py` | `GET /results/user/{id}` |
| Notifications | `NotificationBell.tsx`, `notifications.py` | `GET /notifications/` |
| Analytics | `Progress.tsx`, `users.py` | `GET /users/{id}/analytics` |

### Database Collections

1. **users** - User profiles with XP, level, badges, streak
2. **assessment_submissions** - Assessment results
3. **coding_solutions** - Coding problem solutions
4. **notifications** - User notifications
5. **user_stats** - Detailed statistics

---

**[Back to Features Overview](./FEATURES_OVERVIEW.md)** | **[Next: Admin Features →](./ADMIN_FEATURES.md)**


