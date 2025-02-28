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
            <img src={user.avatar} alt={user.name} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-600 dark:text-gray-300">
              {user.name.charAt(0).toUpperCase()}
            </div>
          )}
        </div>
        <div className="ml-3 flex-1">
          <div className="font-medium text-gray-900 dark:text-white">{user.name}</div>
          <div className="text-sm text-gray-500 dark:text-gray-400">设置</div>
        </div>
      </div>
    </div>
  );
}; 