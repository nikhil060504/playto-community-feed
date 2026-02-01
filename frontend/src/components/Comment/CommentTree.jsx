import { useState } from 'react';
import { commentsAPI } from '../../services/api';
import CreateComment from './CreateComment';

export default function CommentTree({ comment, postId, onUpdate, depth = 0 }) {
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [liking, setLiking] = useState(false);
  const [currentComment, setCurrentComment] = useState(comment);

  const handleLike = async (e) => {
    e.stopPropagation();
    setLiking(true);

    try {
      const { data } = await commentsAPI.like(currentComment.id);
      setCurrentComment({
        ...currentComment,
        is_liked: data.is_liked,
        like_count: data.like_count
      });
    } catch (error) {
      console.error('Failed to like comment:', error);
    } finally {
      setLiking(false);
    }
  };

  const handleReplyCreated = () => {
    setShowReplyForm(false);
    onUpdate();
  };

  // Simple indentation for nested comments
  const indentClass = depth > 0 ? `ml-${Math.min(depth, 6) * 4} border-l-2 border-gray-200 pl-4` : '';

  return (
    <div className={`${indentClass} ${depth > 0 ? 'mt-3' : ''}`}>
      <div className="bg-white rounded-lg shadow-sm p-4">
        {/* Author Info */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center text-white text-sm font-bold">
              {currentComment?.author?.username?.[0]?.toUpperCase() || '?'}
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">
                {currentComment?.author?.username || 'Unknown'}
              </p>
              <p className="text-xs text-gray-500">
                {currentComment?.created_at ? new Date(currentComment.created_at).toLocaleString() : 'Unknown date'} • Depth: {currentComment?.depth ?? 0}
              </p>
            </div>
          </div>
        </div>

        {/* Content */}
        <p className="text-gray-800 mb-3">
          {currentComment?.content || ''}
        </p>

        {/* Actions */}
        <div className="flex items-center space-x-3">
          <button
            onClick={handleLike}
            disabled={liking}
            className={`flex items-center space-x-1 px-3 py-1 rounded text-sm transition ${
              currentComment?.is_liked
                ? 'bg-red-50 text-red-600'
                : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
            }`}
          >
            <span>{currentComment?.is_liked ? '❤️' : '🤍'}</span>
            <span>{currentComment?.like_count ?? 0}</span>
          </button>

          {/* Only allow replies if depth is less than 4 to keep it simple */}
          {(currentComment?.depth ?? 0) < 4 && (
            <button
              onClick={() => setShowReplyForm(!showReplyForm)}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              {showReplyForm ? 'Cancel' : 'Reply'}
            </button>
          )}
        </div>

        {/* Reply Form */}
        {showReplyForm && (
          <div className="mt-4">
            <CreateComment
              postId={postId}
              parentId={currentComment.id}
              onCommentCreated={handleReplyCreated}
              onCancel={() => setShowReplyForm(false)}
            />
          </div>
        )}
      </div>

      {/* Nested Replies - Recursive rendering */}
      {currentComment.replies && currentComment.replies.length > 0 && (
        <div className="mt-2 space-y-2">
          {currentComment.replies.map((reply) => (
            <CommentTree
              key={reply.id}
              comment={reply}
              postId={postId}
              onUpdate={onUpdate}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}
