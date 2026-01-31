import { useState, useEffect } from 'react';
import { leaderboardAPI } from '../../services/api';

export default function LeaderboardWidget() {
  const [topUsers, setTopUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeaderboard();
    // Refresh every minute
    const interval = setInterval(loadLeaderboard, 60000);
    return () => clearInterval(interval);
  }, []);

  const loadLeaderboard = async () => {
    try {
      const { data } = await leaderboardAPI.getTop();
      setTopUsers(data);
    } catch (error) {
      console.error('Failed to load leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 sticky top-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">
          🏆 Top Contributors
        </h2>
        <span className="text-xs text-gray-500">Last 24h</span>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      ) : topUsers.length === 0 ? (
        <p className="text-gray-500 text-sm text-center py-8">
          No activity yet
        </p>
      ) : (
        <div className="space-y-4">
          {topUsers.map((user, index) => (
            <div
              key={user.id}
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition"
            >
              {/* Rank Badge */}
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                index === 0 ? 'bg-yellow-100 text-yellow-700' :
                index === 1 ? 'bg-gray-100 text-gray-700' :
                index === 2 ? 'bg-orange-100 text-orange-700' :
                'bg-blue-50 text-blue-700'
              }`}>
                {index + 1}
              </div>

              {/* User Info */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user.username}
                </p>
                {user.bio && (
                  <p className="text-xs text-gray-500 truncate">
                    {user.bio}
                  </p>
                )}
              </div>

              {/* Karma */}
              <div className="flex-shrink-0">
                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {user.karma_24h} 🔥
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <p className="text-xs text-gray-600 text-center">
          <span className="font-medium">Karma Points:</span><br />
          Post Like = 5 points<br />
          Comment Like = 1 point
        </p>
      </div>
    </div>
  );
}
