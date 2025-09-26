import React from 'react';
import { Switch } from 'antd';
import { BulbOutlined, BulbFilled } from '@ant-design/icons';
import { useAppSelector, useAppDispatch } from '../hooks/redux';
import { toggleTheme } from '../store/slices/systemSlice';
import { useTranslation } from 'react-i18next';

/**
 * 主題切換器組件
 * 允許用戶在亮色和暗色主題之間切換
 */
const ThemeToggle: React.FC = () => {
  const dispatch = useAppDispatch();
  const { t } = useTranslation();
  const theme = useAppSelector((state) => state.system.theme);

  const handleToggleTheme = () => {
    dispatch(toggleTheme());
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      {theme === 'light' ? (
        <BulbOutlined style={{ color: '#faad14' }} />
      ) : (
        <BulbFilled style={{ color: '#faad14' }} />
      )}
      <Switch
        checked={theme === 'dark'}
        onChange={handleToggleTheme}
        checkedChildren={t('common.dark')}
        unCheckedChildren={t('common.light')}
      />
    </div>
  );
};

export default ThemeToggle;