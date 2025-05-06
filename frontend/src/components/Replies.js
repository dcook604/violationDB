import React from 'react';

export default function Replies({ replies, loadingReplies, fetchReplies }) {
  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold mb-2">Replies</h3>
      {loadingReplies ? (
        <div>Loading replies...</div>
      ) : (
        <>
          {replies.length === 0 ? (
            <div className="text-gray-500">No replies yet.</div>
          ) : (
            <ul className="space-y-2">
              {replies.map((reply, idx) => (
                <li key={idx} className="bg-gray-100 rounded p-2">
                  <div className="text-sm text-gray-700">{reply.message}</div>
                  <div className="text-xs text-gray-500 mt-1">By {reply.author} on {new Date(reply.created_at).toLocaleString()}</div>
                </li>
              ))}
            </ul>
          )}
          <button onClick={fetchReplies} className="mt-2 text-blue-600 hover:underline text-xs">Refresh Replies</button>
        </>
      )}
    </div>
  );
} 