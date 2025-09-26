/**
 * 主佈局組件
 * @author TRAE
 * @description 應用程序主佈局，包含側邊欄、頂部導航和內容區域
 */

import React, { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, Space, Button, Switch, theme } from 'antd';
import { 
  MenuFoldOutlined, 
  MenuUnfoldOutlined,
  UserOutlined,
  GlobalOutlined,
  SettingOutlined,
  LogoutOutlined
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import type { MenuProps } from 'antd';
import { useAppSelector, useAppDispatch } from '../hooks/redux';
import { toggleTheme } from '../store/slices/systemSlice';

const { Header, Sider, Content } = Layout;

/**
 * 主佈局組件
 * @description 提供應用程序的整體佈局結構，包括響應式側邊欄和頂部導航
 */
const MainLayout: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const dispatch = useAppDispatch();
  const themeMode = useAppSelector((state) => state.system.theme);
  
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  // 語言切換選項
  const languageOptions: MenuProps['items'] = [
    {
      key: 'zh-TW',
      label: '繁體中文',
      onClick: () => i18n.changeLanguage('zh-TW')
    },
    {
      key: 'zh-CN',
      label: '简体中文',
      onClick: () => i18n.changeLanguage('zh-CN')
    },
    {
      key: 'en',
      label: 'English',
      onClick: () => i18n.changeLanguage('en')
    }
  ];

  // 用戶菜單選項
  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: t('common.profile')
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: t('common.settings')
    },
    {
      type: 'divider'
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: t('common.logout'),
      danger: true
    }
  ];

  // 導航菜單項
  const menuItems: MenuProps['items'] = [
    {
      key: '/dashboard',
      icon: <span className="anticon">📊</span>,
      label: t('navigation.dashboard')
    },
    {
      key: '/proxy',
      icon: <span className="anticon">🌐</span>,
      label: t('navigation.proxyManagement')
    },
    {
      key: '/monitor',
      icon: <span className="anticon">📈</span>,
      label: t('navigation.systemMonitor')
    },
    {
      key: '/config',
      icon: <span className="anticon">⚙️</span>,
      label: t('navigation.configuration')
    },
    {
      key: '/logs',
      icon: <span className="anticon">📝</span>,
      label: t('navigation.logs')
    }
  ];

  // 菜單點擊處理
  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    navigate(key);
  };

  // 用戶菜單點擊處理
  const handleUserMenuClick: MenuProps['onClick'] = ({ key }) => {
    switch (key) {
      case 'logout':
        navigate('/login');
        break;
      case 'profile':
        navigate('/profile');
        break;
      case 'settings':
        navigate('/settings');
        break;
    }
  };

  // 獲取當前選中的菜單項
  const getSelectedKey = () => {
    const path = location.pathname;
    if (path.startsWith('/proxy')) return '/proxy';
    if (path.startsWith('/monitor')) return '/monitor';
    if (path.startsWith('/config')) return '/config';
    if (path.startsWith('/logs')) return '/logs';
    return '/dashboard';
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div className="logo" style={{ 
          height: '64px', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          color: 'white',
          fontSize: collapsed ? '16px' : '20px',
          fontWeight: 'bold',
          backgroundColor: themeMode === 'dark' ? '#141414' : '#001529'
        }}>
          {collapsed ? '🚀' : 'Proxy Manager'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[getSelectedKey()]}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ borderRight: 0 }}
        />
      </Sider>
      
      <Layout style={{ marginLeft: collapsed ? 80 : 200 }}>
        <Header style={{ 
          padding: '0 24px', 
          background: colorBgContainer,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{ fontSize: '16px' }}
          />
          
          <Space>
            {/* 語言切換 */}
            <Dropdown 
              menu={{ items: languageOptions }} 
              placement="bottomRight"
              arrow
            >
              <Button type="text" icon={<GlobalOutlined />}>
                {i18n.language === 'zh-TW' ? '繁體' : 
                 i18n.language === 'zh-CN' ? '简体' : 'EN'}
              </Button>
            </Dropdown>
            
            {/* 主題切換 */}
            <Space size="small">
              <span>{themeMode === 'dark' ? '🌙' : '🌞'}</span>
              <Switch 
                checked={themeMode === 'dark'}
                onChange={() => dispatch(toggleTheme())}
                checkedChildren={t('common.dark')}
                unCheckedChildren={t('common.light')}
              />
            </Space>
            
            {/* 用戶菜單 */}
            <Dropdown 
              menu={{ items: userMenuItems, onClick: handleUserMenuClick }} 
              placement="bottomRight"
              arrow
            >
              <Space style={{ cursor: 'pointer' }}>
                <Avatar icon={<UserOutlined />} />
                <span>管理員</span>
              </Space>
            </Dropdown>
          </Space>
        </Header>
        
        <Content style={{ 
          margin: '24px 16px', 
          padding: 24, 
          minHeight: 280,
          background: colorBgContainer,
          borderRadius: borderRadiusLG,
          overflow: 'auto'
        }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;