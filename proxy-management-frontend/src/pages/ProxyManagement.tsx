/**
 * 代理管理頁面組件
 * @author TRAE
 * @description 代理列表管理，包含搜索、篩選、批量操作等功能
 */

import React, { useState } from 'react';
import { 
  Card, 
  Table, 
  Button, 
  Space, 
  Input, 
  Select, 
  Tag, 
  Modal,
  Form,
  Row,
  Col,
  message,
  Tooltip,
  Badge,
  Dropdown
} from 'antd';
import type { MenuProps } from 'antd';
import { 
  SearchOutlined, 
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  QuestionCircleOutlined,
  ExportOutlined,
  ImportOutlined,
  ReloadOutlined,
  MoreOutlined
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import type { Proxy } from '../types';
import { ProxyStatus, ProxyProtocol } from '../types';

const { Search } = Input;
const { Option } = Select;

/**
 * 代理管理頁面組件
 * @description 管理代理列表，提供搜索、篩選、編輯、刪除等功能
 */
const ProxyManagement: React.FC = () => {
  const { t } = useTranslation();
  const [loading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingProxy, setEditingProxy] = useState<Proxy | null>(null);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [protocolFilter, setProtocolFilter] = useState<string>('');
  const [form] = Form.useForm();

  // 模擬代理數據
  const [proxies, setProxies] = useState<Proxy[]>([
    {
      id: '1',
      host: '192.168.1.100',
      port: 8080,
      protocol: ProxyProtocol.HTTP,
      status: ProxyStatus.VALID,
      country: 'United States',
      city: 'New York',
      responseTime: 120,
      anonymity: 'elite',
      lastChecked: new Date('2024-01-15 14:30:25'),
      createdAt: new Date('2024-01-10 10:00:00'),
      updatedAt: new Date('2024-01-15 14:30:25')
    },
    {
      id: '2',
      host: '203.0.113.45',
      port: 3128,
      protocol: ProxyProtocol.HTTPS,
      status: ProxyStatus.INVALID,
      country: 'Japan',
      city: 'Tokyo',
      responseTime: 0,
      anonymity: 'anonymous',
      lastChecked: new Date('2024-01-15 14:25:10'),
      createdAt: new Date('2024-01-12 15:30:00'),
      updatedAt: new Date('2024-01-15 14:25:10')
    },
    {
      id: '3',
      host: '198.51.100.25',
      port: 1080,
      protocol: ProxyProtocol.SOCKS5,
      status: ProxyStatus.VALID,
      country: 'Germany',
      city: 'Berlin',
      responseTime: 85,
      anonymity: 'elite',
      lastChecked: new Date('2024-01-15 14:20:45'),
      createdAt: new Date('2024-01-08 09:15:00'),
      updatedAt: new Date('2024-01-15 14:20:45')
    },
    {
      id: '4',
      host: '10.0.0.50',
      port: 8081,
      protocol: ProxyProtocol.SOCKS4,
      status: ProxyStatus.TEMPORARILY_INVALID,
      country: 'United Kingdom',
      city: 'London',
      responseTime: 2500,
      anonymity: 'transparent',
      lastChecked: new Date('2024-01-15 14:15:30'),
      createdAt: new Date('2024-01-11 16:45:00'),
      updatedAt: new Date('2024-01-15 14:15:30')
    }
  ]);

  // 獲取狀態標籤
  const getStatusTag = (status: ProxyStatus) => {
    switch (status) {
      case ProxyStatus.VALID:
        return <Tag color="success" icon={<CheckCircleOutlined />}>{t('proxy.status.valid')}</Tag>;
      case ProxyStatus.INVALID:
        return <Tag color="error" icon={<CloseCircleOutlined />}>{t('proxy.status.invalid')}</Tag>;
      case ProxyStatus.TEMPORARILY_INVALID:
        return <Tag color="warning" icon={<ClockCircleOutlined />}>{t('proxy.status.temporarily_invalid')}</Tag>;
      case ProxyStatus.UNTESTED:
        return <Tag color="default" icon={<QuestionCircleOutlined />}>{t('proxy.status.untested')}</Tag>;
      default:
        return <Tag>{status}</Tag>;
    }
  };

  // 獲取協議標籤
  const getProtocolTag = (protocol: ProxyProtocol) => {
    const colors = {
      [ProxyProtocol.HTTP]: 'blue',
      [ProxyProtocol.HTTPS]: 'green',
      [ProxyProtocol.SOCKS4]: 'orange',
      [ProxyProtocol.SOCKS5]: 'purple'
    };
    return <Tag color={colors[protocol]}>{protocol.toUpperCase()}</Tag>;
  };

  // 獲取匿名度標籤
  const getAnonymityTag = (anonymity: string) => {
    const colors = {
      'elite': 'red',
      'anonymous': 'orange',
      'transparent': 'blue'
    };
    return <Tag color={colors[anonymity as keyof typeof colors]}>{anonymity}</Tag>;
  };

  // 表格列配置
  const columns: Array<{
    title: string;
    dataIndex?: string;
    key: string;
    width?: number;
    fixed?: boolean | 'left' | 'right';
    render?: (value: any, record: Proxy) => React.ReactNode;
  }> = [
    {
      title: t('proxy.host'),
      dataIndex: 'host',
      key: 'host',
      width: 140,
      render: (text: string, record: Proxy) => (
        <Space>
          <Badge 
            status={record.status === ProxyStatus.VALID ? 'success' : 
                   record.status === ProxyStatus.INVALID ? 'error' : 'warning'} 
          />
          <span>{text}</span>
        </Space>
      )
    },
    {
      title: t('proxy.port'),
      dataIndex: 'port',
      key: 'port',
      width: 80,
      render: (port: number) => <Tag color="blue">{port}</Tag>
    },
    {
      title: t('proxy.protocol'),
      dataIndex: 'protocol',
      key: 'protocol',
      width: 100,
      render: (protocol: ProxyProtocol) => getProtocolTag(protocol)
    },
    {
      title: t('proxy.status'),
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: ProxyStatus) => getStatusTag(status)
    },
    {
      title: t('proxy.country'),
      dataIndex: 'country',
      key: 'country',
      width: 120
    },
    {
      title: t('proxy.city'),
      dataIndex: 'city',
      key: 'city',
      width: 100
    },
    {
      title: t('proxy.responseTime'),
      dataIndex: 'responseTime',
      key: 'responseTime',
      width: 100,
      render: (time: number) => {
        if (time === 0) return <span>-</span>;
        const color = time < 500 ? '#52c41a' : time < 1000 ? '#faad14' : '#ff4d4f';
        return <span style={{ color, fontWeight: 'bold' }}>{time}ms</span>;
      }
    },
    {
      title: t('proxy.anonymity'),
      dataIndex: 'anonymity',
      key: 'anonymity',
      width: 100,
      render: (anonymity: string) => getAnonymityTag(anonymity)
    },
    {
      title: t('proxy.lastChecked'),
      dataIndex: 'lastChecked',
      key: 'lastChecked',
      width: 160
    },
    {
      title: t('common.actions'),
      key: 'actions',
      width: 150,
      fixed: 'right',
      render: (_: any, record: Proxy) => {
        const moreItems: MenuProps['items'] = [
          {
            key: 'view',
            label: t('proxy.viewDetails'),
            icon: <SearchOutlined />
          },
          {
            key: 'history',
            label: t('proxy.validationHistory'),
            icon: <ReloadOutlined />
          },
          {
            type: 'divider'
          },
          {
            key: 'delete',
            label: t('common.delete'),
            icon: <DeleteOutlined />,
            danger: true
          }
        ];

        return (
          <Space size="small">
            <Tooltip title={t('proxy.validate')}>
              <Button 
                type="link" 
                size="small" 
                icon={<CheckCircleOutlined />}
                onClick={() => handleValidate(record.id)}
              />
            </Tooltip>
            <Tooltip title={t('common.edit')}>
              <Button 
                type="link" 
                size="small" 
                icon={<EditOutlined />}
                onClick={() => handleEdit(record)}
              />
            </Tooltip>
            <Dropdown menu={{ items: moreItems, onClick: ({ key }) => handleMoreAction(key, record) }}>
              <Button type="link" size="small" icon={<MoreOutlined />} />
            </Dropdown>
          </Space>
        );
      }
    }
  ];

  // 處理更多操作
  const handleMoreAction = (key: string, record: Proxy) => {
    switch (key) {
      case 'view':
        // 查看詳情
        message.info(`查看代理 ${record.host}:${record.port} 的詳情`);
        break;
      case 'history':
        // 查看歷史
        message.info(`查看代理 ${record.host}:${record.port} 的驗證歷史`);
        break;
      case 'delete':
        handleDelete(record.id);
        break;
    }
  };

  // 處理搜索
  const handleSearch = (value: string) => {
    setSearchText(value);
  };

  // 處理編輯
  const handleEdit = (proxy: Proxy) => {
    setEditingProxy(proxy);
    form.setFieldsValue(proxy);
    setModalVisible(true);
  };

  // 處理新增
  const handleAdd = () => {
    setEditingProxy(null);
    form.resetFields();
    setModalVisible(true);
  };

  // 處理刪除
  const handleDelete = (id: string) => {
    Modal.confirm({
      title: t('common.delete'),
      content: `確定要刪除代理嗎？`,
      onOk: () => {
        setProxies(prev => prev.filter(proxy => proxy.id !== id));
        message.success('代理刪除成功');
      }
    });
  };

  // 處理驗證
  const handleValidate = (id: string) => {
    message.loading('正在驗證代理...', 2);
    setTimeout(() => {
      message.success('代理驗證完成');
      // 更新代理狀態
      setProxies(prev => prev.map(proxy => 
        proxy.id === id 
          ? { ...proxy, status: Math.random() > 0.3 ? ProxyStatus.VALID : ProxyStatus.INVALID, lastChecked: new Date() }
          : proxy
      ));
    }, 2000);
  };

  // 處理批量驗證
  const handleBatchValidate = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('請選擇要驗證的代理');
      return;
    }
    message.loading(`正在驗證 ${selectedRowKeys.length} 個代理...`, 3);
    setTimeout(() => {
      message.success(`批量驗證完成，${selectedRowKeys.length} 個代理已更新`);
      setSelectedRowKeys([]);
    }, 3000);
  };

  // 處理批量刪除
  const handleBatchDelete = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('請選擇要刪除的代理');
      return;
    }
    Modal.confirm({
      title: t('common.delete'),
      content: `確定要刪除選中的 ${selectedRowKeys.length} 個代理嗎？`,
      onOk: () => {
        setProxies(prev => prev.filter(proxy => !selectedRowKeys.includes(proxy.id)));
        setSelectedRowKeys([]);
        message.success(`批量刪除完成，${selectedRowKeys.length} 個代理已刪除`);
      }
    });
  };

  // 處理表單提交
  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingProxy) {
        // 編輯模式
        setProxies(prev => prev.map(proxy => 
          proxy.id === editingProxy.id 
            ? { ...proxy, ...values, updatedAt: new Date() }
            : proxy
        ));
        message.success('代理更新成功');
      } else {
        // 新增模式
        const newProxy: Proxy = {
          id: Date.now().toString(),
          ...values,
          status: ProxyStatus.UNTESTED,
          createdAt: new Date(),
          updatedAt: new Date()
        };
        setProxies(prev => [...prev, newProxy]);
        message.success('代理新增成功');
      }
      setModalVisible(false);
      form.resetFields();
    } catch (error) {
      console.error('表單驗證失敗:', error);
    }
  };

  // 處理表單取消
  const handleModalCancel = () => {
    setModalVisible(false);
    form.resetFields();
  };

  // 行選擇配置
  const rowSelection = {
    selectedRowKeys,
    onChange: (newSelectedRowKeys: React.Key[]) => {
      setSelectedRowKeys(newSelectedRowKeys);
    }
  };

  // 篩選數據
  const filteredProxies = proxies.filter(proxy => {
    const matchesSearch = !searchText || 
      proxy.host.toLowerCase().includes(searchText.toLowerCase()) ||
      (proxy.country && proxy.country.toLowerCase().includes(searchText.toLowerCase())) ||
      (proxy.city && proxy.city.toLowerCase().includes(searchText.toLowerCase()));
    
    const matchesStatus = !statusFilter || proxy.status === statusFilter;
    const matchesProtocol = !protocolFilter || proxy.protocol === protocolFilter;
    
    return matchesSearch && matchesStatus && matchesProtocol;
  });

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        {/* 搜索和操作區域 */}
        <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <Space size="middle" wrap>
            <Search
              placeholder="搜索主機、國家或城市"
              allowClear
              enterButton={<SearchOutlined />}
              style={{ width: 250 }}
              onSearch={handleSearch}
            />
            <Select
              placeholder="狀態篩選"
              style={{ width: 120 }}
              allowClear
              value={statusFilter}
              onChange={setStatusFilter}
            >
              <Option value="">全部狀態</Option>
              <Option value={ProxyStatus.VALID}>{t('proxy.status.valid')}</Option>
              <Option value={ProxyStatus.INVALID}>{t('proxy.status.invalid')}</Option>
              <Option value={ProxyStatus.TEMPORARILY_INVALID}>{t('proxy.status.temporarily_invalid')}</Option>
              <Option value={ProxyStatus.UNTESTED}>{t('proxy.status.untested')}</Option>
            </Select>
            <Select
              placeholder="協議篩選"
              style={{ width: 120 }}
              allowClear
              value={protocolFilter}
              onChange={setProtocolFilter}
            >
              <Option value="">全部協議</Option>
              <Option value={ProxyProtocol.HTTP}>HTTP</Option>
              <Option value={ProxyProtocol.HTTPS}>HTTPS</Option>
              <Option value={ProxyProtocol.SOCKS4}>SOCKS4</Option>
              <Option value={ProxyProtocol.SOCKS5}>SOCKS5</Option>
            </Select>
          </Space>
          
          <Space>
            {selectedRowKeys.length > 0 && (
              <Space>
                <Button icon={<CheckCircleOutlined />} onClick={handleBatchValidate}>
                  {t('proxy.batchValidate')} ({selectedRowKeys.length})
                </Button>
                <Button danger icon={<DeleteOutlined />} onClick={handleBatchDelete}>
                  {t('proxy.batchDelete')} ({selectedRowKeys.length})
                </Button>
              </Space>
            )}
            <Button icon={<ExportOutlined />}>
              {t('proxy.exportProxies')}
            </Button>
            <Button icon={<ImportOutlined />}>
              {t('proxy.importProxies')}
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              {t('proxy.addProxy')}
            </Button>
          </Space>
        </div>

        {/* 代理表格 */}
        <Table
          rowSelection={rowSelection}
          columns={columns}
          dataSource={filteredProxies}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1200 }}
          pagination={{
            total: filteredProxies.length,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} / ${total}`
          }}
        />
      </Card>

      {/* 新增/編輯模態框 */}
      <Modal
        title={editingProxy ? t('proxy.editProxy') : t('proxy.addProxy')}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            protocol: ProxyProtocol.HTTP,
            port: 8080
          }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="host"
                label={t('proxy.host')}
                rules={[{ required: true, message: t('validation.required') }]}
              >
                <Input placeholder="例如: 192.168.1.1" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="port"
                label={t('proxy.port')}
                rules={[
                  { required: true, message: t('validation.required') },
                  { type: 'number', min: 1, max: 65535, message: t('validation.invalidPort') }
                ]}
              >
                <Input type="number" placeholder="1-65535" />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="protocol"
                label={t('proxy.protocol')}
                rules={[{ required: true, message: t('validation.required') }]}
              >
                <Select>
                  <Option value={ProxyProtocol.HTTP}>HTTP</Option>
                  <Option value={ProxyProtocol.HTTPS}>HTTPS</Option>
                  <Option value={ProxyProtocol.SOCKS4}>SOCKS4</Option>
                  <Option value={ProxyProtocol.SOCKS5}>SOCKS5</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="anonymity"
                label={t('proxy.anonymity')}
              >
                <Select allowClear>
                  <Option value="transparent">{t('proxy.anonymity.transparent')}</Option>
                  <Option value="anonymous">{t('proxy.anonymity.anonymous')}</Option>
                  <Option value="elite">{t('proxy.anonymity.elite')}</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="country"
                label={t('proxy.country')}
              >
                <Input placeholder="例如: China" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="city"
                label={t('proxy.city')}
              >
                <Input placeholder="例如: Beijing" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default ProxyManagement;