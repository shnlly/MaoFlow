import React from 'react';
import { User } from './types';

interface UserProfileProps {
  user: User;
  onSettingsClick: () => void;
}

export const UserProfile: React.FC<UserProfileProps> = ({ user, onSettingsClick }) => {
  return (
    <div className="p-4 border-t border-gray-200 dark:border-gray-700">
      <div
        className="flex items-center cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 p-2 rounded-lg"
        onClick={onSettingsClick}
      >
        <div className="w-10 h-10 rounded-full bg-gray-300 dark:bg-gray-600 overflow-hidden">
          {user.avatar ? (
            <img src={user.avatar} alt={user.nickname} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-600 dark:text-gray-300">
              {user.nickname.charAt(0).toUpperCase()}
            </div>
          )}
        </div>
        <div className="ml-3 flex-1">
          <div className="font-medium text-gray-900 dark:text-white">{user.nickname}</div>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            会话: {user.conversation_count} | 消息: {user.message_count}
          </div>
        </div>
        <div className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
      </div>
    </div>
  );
}; 