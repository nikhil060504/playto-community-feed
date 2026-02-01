import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { postsAPI, commentsAPI } from '../services/api';
import CommentTree from '../components/Comment/CommentTree';
import CreateComment from '../components/Comment/CreateComment';

export default function PostDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPost();
    loadComments();
  }, [id]);

  const loadPost = async () => {
    try {
      const { data } = await postsAPI.getById(id);
      setPost(data);
    } catch (error) {
      console.error('Failed to load post:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadComments = async () => {
    try {
      const { data } = await commentsAPI.getByPost(id);
      // Handle both array response and paginated response with 'results'
      const comments = Array.isArray(data) ? data : (data?.results || []);
      // Filter out any invalid comments that might cause crashes
      const validComments = comments.filter(c => c && c.id && c.author);
      setComments(validComments);
    } catch (error) {
      console.error('Failed to load comments:', error);
      setComments([]); // Set empty array on error
    }
  };

  const handleLike = async () => {
    try {
      const { data } = await postsAPI.like(post.id);
      setPost({
        ...post,
        is_liked: data.is_liked,
        like_count: data.like_count
      });
    } catch (error) {
      console.error('Failed to like post:', error);
    }
  };

  const handleCommentCreated = () => {
    loadComments();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Post not found</p>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Feed
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <button
            onClick={() => navigate('/')}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition"
          >
            <span>←</span>
            <span>Back to Feed</span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Post */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          {/* Author Info */}
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-lg">
              {post?.author?.username?.[0]?.toUpperCase() || '?'}
            </div>
            <div>
              <p className="font-medium text-gray-900">
                {post?.author?.username || 'Unknown'}
              </p>
              <p className="text-sm text-gray-500">
                {post?.created_at ? new Date(post.created_at).toLocaleString() : 'Unknown date'}
              </p>
            </div>
          </div>

          {/* Content */}
          <p className="text-gray-800 text-lg mb-6 whitespace-pre-wrap">
            {post?.content || ''}
          </p>

          {/* Actions */}
          <div className="flex items-center space-x-4 pt-4 border-t">
            <button
              onClick={handleLike}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition ${
                post?.is_liked
                  ? 'bg-red-50 text-red-600 hover:bg-red-100'
                  : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
              }`}
            >
              <span className="text-lg">{post?.is_liked ? '❤️' : '🤍'}</span>
              <span className="font-medium">{post?.like_count ?? 0}</span>
            </button>

            <div className="flex items-center space-x-2 text-gray-600">
              <span>💬</span>
              <span className="text-sm">{comments.length} comments</span>
            </div>
          </div>
        </div>

        {/* Create Comment */}
        {post?.id && <CreateComment postId={post.id} onCommentCreated={handleCommentCreated} />}

        {/* Comments */}
        <div className="mt-6 space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Comments ({comments.length})
          </h3>

          {comments.length === 0 ? (
            <div className="bg-white rounded-lg shadow-sm p-8 text-center">
              <p className="text-gray-500">No comments yet. Be the first to comment!</p>
            </div>
          ) : (
            comments.map((comment) => (
              <CommentTree
                key={comment.id}
                comment={comment}
                postId={post.id}
                onUpdate={loadComments}
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
}
