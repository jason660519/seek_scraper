/**
 * 登入頁面組件
 * @author TRAE
 * @description 用戶登入頁面，包含語言切換、驗證碼等功能
 */

import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Card, Row, Col, message, Space, Select } from 'antd';
import { UserOutlined, LockOutlined, SafetyCertificateOutlined, GlobalOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { login } from '../store/slices/authSlice';

const { Option } = Select;

/**
 * 登入頁面組件
 * @description 提供用戶登入功能，包含表單驗證、語言切換、驗證碼等
 */
const Login: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [captcha, setCaptcha] = useState('');
  const [captchaInput, setCaptchaInput] = useState('');

  // 生成驗證碼
  const generateCaptcha = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let result = '';
    for (let i = 0; i < 4; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setCaptcha(result);
  };

  useEffect(() => {
    generateCaptcha();
  }, []);

  // 處理登入
  const handleLogin = async (values: any) => {
    if (captchaInput.toUpperCase() !== captcha) {
      message.error(t('login.captchaRequired'));
      generateCaptcha();
      return;
    }

    setLoading(true);
    
    try {
      // 模擬登入請求
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 模擬登入成功
      if (values.username === 'admin' && values.password === 'admin123') {
        dispatch(login({
          username: values.username,
          token: 'mock-jwt-token-' + Date.now(),
          expiresIn: 3600
        }));
        
        message.success(t('login.loginSuccess'));
        navigate('/dashboard');
      } else {
        message.error(t('login.invalidCredentials'));
        generateCaptcha();
      }
    } catch (error) {
      message.error(t('error.networkError'));
    } finally {
      setLoading(false);
    }
  };

  // 處理語言切換
  const handleLanguageChange = (value: string) => {
    i18n.changeLanguage(value);
  };

  return (
    <div className="login-container">
      <Row justify="center" align="middle" style={{ width: '100%', minHeight: '100vh', padding: '20px' }}>
        <Col xs={24} sm={20} md={16} lg={12} xl={8} xxl={6}>
          <Card
            style={{
              borderRadius: '12px',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
              backdropFilter: 'blur(10px)',
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              maxWidth: '480px',
              margin: '0 auto'
            }}
            styles={{ body: { padding: '32px 24px' } }}
            className="login-card"
          >
            {/* 標題和語言切換 */}
            <div style={{ textAlign: 'center', marginBottom: '24px' }}>
              <div style={{ 
                width: '56px', 
                height: '56px', 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                borderRadius: '50%',
                margin: '0 auto 12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '22px',
                color: 'white',
                boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)'
              }}>
                🚀
              </div>
              <h1 style={{ 
                fontSize: '26px', 
                fontWeight: 'bold', 
                margin: '0 0 6px 0',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                {t('login.title')}
              </h1>
              <p style={{ color: '#666', margin: 0, fontSize: '14px' }}>{t('login.subtitle')}</p>
            </div>

            {/* 語言切換 */}
            <div style={{ textAlign: 'right', marginBottom: '20px' }}>
              <Space>
                <GlobalOutlined style={{ color: '#666', fontSize: '14px' }} />
                <Select
                  value={i18n.language}
                  onChange={handleLanguageChange}
                  style={{ width: 110 }}
                  bordered={false}
                  suffixIcon={null}
                  size="small"
                >
                  <Option value="zh-TW">🇹🇼 繁體</Option>
                  <Option value="zh-CN">🇨🇳 简体</Option>
                  <Option value="en">🇺🇸 EN</Option>
                </Select>
              </Space>
            </div>

            {/* 登入表單 */}
            <Form
              name="login"
              size="large"
              onFinish={handleLogin}
              autoComplete="off"
              style={{ maxWidth: '400px', margin: '0 auto' }}
            >
              <Form.Item
                name="username"
                rules={[
                  { required: true, message: t('validation.required') },
                  { min: 3, message: t('validation.minLength', { count: 3 }) },
                  { max: 20, message: t('validation.maxLength', { count: 20 }) }
                ]}
              >
                <Input
                  name="username"
                  prefix={<UserOutlined style={{ color: '#ccc' }} />}
                  placeholder={t('login.username')}
                  style={{
                    borderRadius: '8px',
                    border: '1px solid #d9d9d9',
                    transition: 'all 0.3s'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#d9d9d9'}
                />
              </Form.Item>

              <Form.Item
                name="password"
                rules={[
                  { required: true, message: t('validation.required') },
                  { min: 6, message: t('validation.minLength', { count: 6 }) }
                ]}
              >
                <Input.Password
                  name="password"
                  prefix={<LockOutlined style={{ color: '#ccc' }} />}
                  placeholder={t('login.password')}
                  style={{
                    borderRadius: '8px',
                    border: '1px solid #d9d9d9',
                    transition: 'all 0.3s'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#d9d9d9'}
                />
              </Form.Item>

              {/* 驗證碼 */}
              <Form.Item
                name="captcha"
                rules={[{ required: true, message: t('login.captchaRequired') }]}
              >
                <div className="captcha-container">
                  <Input
                    name="captcha"
                    prefix={<SafetyCertificateOutlined style={{ color: '#ccc' }} />}
                    placeholder={t('login.captcha')}
                    value={captchaInput}
                    onChange={(e) => setCaptchaInput(e.target.value)}
                    style={{
                      borderRadius: '8px',
                      border: '1px solid #d9d9d9',
                      flex: 1
                    }}
                  />
                  <div
                    onClick={generateCaptcha}
                    className="captcha-code"
                  >
                    {captcha}
                  </div>
                </div>
              </Form.Item>

              <Form.Item style={{ marginBottom: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Form.Item name="remember" valuePropName="checked" noStyle>
                    <span style={{ color: '#666', fontSize: '14px' }}>{t('login.rememberMe')}</span>
                  </Form.Item>
                  <a 
                    href="#" 
                    style={{ color: '#667eea', fontSize: '14px' }}
                    onClick={(e) => {
                      e.preventDefault();
                      message.info('忘記密碼功能開發中...');
                    }}
                  >
                    {t('login.forgotPassword')}
                  </a>
                </div>
              </Form.Item>

              <Form.Item style={{ marginBottom: '16px', marginTop: '24px' }}>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  style={{
                    width: '100%',
                    height: '45px',
                    borderRadius: '8px',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    border: 'none',
                    fontSize: '16px',
                    fontWeight: 'bold',
                    boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)'
                  }}
                >
                  {t('login.loginButton')}
                </Button>
              </Form.Item>
            </Form>

            {/* 提示信息 */}
            <div style={{ 
              textAlign: 'center', 
              color: '#666', 
              fontSize: '14px',
              padding: '16px',
              backgroundColor: '#f6f7ff',
              borderRadius: '8px',
              marginTop: '16px'
            }}>
              <p style={{ margin: '0 0 8px 0' }}>測試賬號：</p>
              <p style={{ margin: 0, fontFamily: 'monospace' }}>用戶名：admin / 密碼：admin123</p>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Login;