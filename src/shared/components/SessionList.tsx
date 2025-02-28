import React from 'react';
import { ChatSession } from './types';

interface SessionListProps {
  sessions: ChatSession[];
  currentSessionId?: string;
  onSessionSelect: (session: ChatSession) => void;
  onNewSession: () => void;
  onDeleteSession: (sessionId: string) => void;
}

export const SessionList: React.FC<SessionListProps> = ({
  sessions,
  currentSessionId,
  onSessionSelect,
  onNewSession,
  onDeleteSession,
}) => {
  return (
    <div className="w-64 h-full bg-gray-50 dark:bg-gray-800 flex flex-col">
      <div className="p-4">
        <button
          onClick={onNewSession}
          className="w-full py-2 px-4 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          新建会话
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        {sessions.map((session) => (
          <div
            key={session.id}
            className={`p-4 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 ${
              currentSessionId === session.id ? 'bg-gray-200 dark:bg-gray-600' : ''
            }`}
            onClick={() => onSessionSelect(session)}
          >
            <div className="flex justify-between items-center">
              <div className="flex-1">
                <h3 className="font-medium text-gray-900 dark:text-white truncate">
                  {session.title}
                </h3>
                {session.lastMessage && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                    {session.lastMessage}
                  </p>
                )}
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteSession(session.id);
                }}
                className="ml-2 text-gray-400 hover:text-red-500"
              >
                删除
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}; 