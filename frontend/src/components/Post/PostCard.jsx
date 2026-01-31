import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { postsAPI } from '../../services/api';

export default function PostCard({ post, onUpdate }) {
  const [liking, setLiking] = useState(false);
  const [currentPost, setCurrentPost] = useState(post);
  const navigate = useNavigate();

  const handleLike = async (e) => {
    e.stopPropagation();
    setLiking(true);

    try {
      const { data } = await postsAPI.like(currentPost.id);
      setCurrentPost({
        ...currentPost,
        is_liked: data.is_liked,
        like_count: data.like_count
      });
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error('Failed to like post:', error);
    } finally {
      setLiking(false);
    }
  };

  const handleClick = () => {
    navigate(`/post/${currentPost.id}`);
  };

  return (
    <div 
      onClick={handleClick}
      className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition cursor-pointer animate-fade-in"
    >
      {/* Author Info */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white font-bold">
            {currentPost.author.username[0].toUpperCase()}
          </div>
          <div>
            <p className="font-medium text-gray-900">
              {currentPost.author.username}
            </p>
            <p className="text-xs text-gray-500">
              {new Date(currentPost.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <p className="text-gray-800 mb-4 whitespace-pre-wrap">
        {currentPost.content}
      </p>

      {/* Actions */}
      <div className="flex items-center space-x-4 pt-4 border-t">
        <button
          onClick={handleLike}
          disabled={liking}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition ${
            currentPost.is_liked
              ? 'bg-red-50 text-red-600 hover:bg-red-100'
              : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
          }`}
        >
          <span className="text-lg">{currentPost.is_liked ? '❤️' : '🤍'}</span>
          <span className="font-medium">{currentPost.like_count}</span>
        </button>

        <div className="flex items-center space-x-2 text-gray-600">
          <span>💬</span>
          <span className="text-sm">View Comments</span>
        </div>
      </div>
    </div>
  );
}
