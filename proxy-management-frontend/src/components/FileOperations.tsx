/**
 * 文件操作組件
 * @author TRAE
 * @description 處理代理文件的導入導出功能
 */

import React, { useState } from 'react';
import { Button, Upload, Modal, message, Select, Form, Space, Progress } from 'antd';
import { ExportOutlined, ImportOutlined, UploadOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import type { UploadProps } from 'antd';
import type { Proxy, ProxyProtocol, ProxyStatus } from '../types';

const { Option } = Select;

interface FileOperationsProps {
  proxies: Proxy[];
  onImport: (proxies: Proxy[]) => void;
  loading?: boolean;
}

/**
 * 文件操作組件
 */
const FileOperations: React.FC<FileOperationsProps> = ({
  proxies,
  onImport,
  loading = false
}) => {
  const { t } = useTranslation();
  const [exportModalVisible, setExportModalVisible] = useState(false);
  const [importModalVisible, setImportModalVisible] = useState(false);
  const [exportForm] = Form.useForm();
  const [importProgress, setImportProgress] = useState(0);
  const [importing, setImporting] = useState(false);

  // 導出配置
  const exportConfig = {
    formats: [
      { value: 'csv', label: 'CSV', description: '逗號分隔值格式' },
      { value: 'json', label: 'JSON', description: 'JavaScript對象表示法' },
      { value: 'txt', label: 'TXT', description: '純文本格式' },
      { value: 'xml', label: 'XML', description: '可擴展標記語言' }
    ],
    filters: [
      { value: 'all', label: '全部代理' },
      { value: 'valid', label: '僅有效代理' },
      { value: 'invalid', label: '僅無效代理' },
      { value: 'http', label: 'HTTP協議' },
      { value: 'https', label: 'HTTPS協議' },
      { value: 'socks4', label: 'SOCKS4協議' },
      { value: 'socks5', label: 'SOCKS5協議' }
    ]
  };

  // 處理導出
  const handleExport = async (values: any) => {
    try {
      const { format, filter, includeMetadata } = values;
      
      // 根據篩選條件過濾代理
      let filteredProxies = proxies;
      if (filter !== 'all') {
        switch (filter) {
          case 'valid':
            filteredProxies = proxies.filter(p => p.status === 'valid');
            break;
          case 'invalid':
            filteredProxies = proxies.filter(p => p.status === 'invalid');
            break;
          case 'http':
            filteredProxies = proxies.filter(p => p.protocol === 'http');
            break;
          case 'https':
            filteredProxies = proxies.filter(p => p.protocol === 'https');
            break;
          case 'socks4':
            filteredProxies = proxies.filter(p => p.protocol === 'socks4');
            break;
          case 'socks5':
            filteredProxies = proxies.filter(p => p.protocol === 'socks5');
            break;
        }
      }

      // 生成文件名
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `proxies_${filter}_${timestamp}.${format}`;

      // 根據格式生成文件內容
      let content = '';
      let mimeType = '';

      switch (format) {
        case 'csv':
          content = generateCSV(filteredProxies, includeMetadata);
          mimeType = 'text/csv';
          break;
        case 'json':
          content = generateJSON(filteredProxies, includeMetadata);
          mimeType = 'application/json';
          break;
        case 'txt':
          content = generateTXT(filteredProxies);
          mimeType = 'text/plain';
          break;
        case 'xml':
          content = generateXML(filteredProxies, includeMetadata);
          mimeType = 'application/xml';
          break;
      }

      // 下載文件
      downloadFile(content, filename, mimeType);
      
      setExportModalVisible(false);
      exportForm.resetFields();
      message.success(t('proxy.exportSuccess', { count: filteredProxies.length }));
    } catch (error) {
      message.error(t('proxy.exportError'));
      console.error('Export error:', error);
    }
  };

  // 生成CSV內容
  const generateCSV = (proxies: Proxy[], includeMetadata: boolean) => {
    const headers = ['host', 'port', 'protocol', 'status', 'country', 'city', 'responseTime', 'anonymity'];
    if (includeMetadata) {
      headers.push('createdAt', 'updatedAt', 'lastChecked');
    }

    const csvContent = [
      headers.join(','),
      ...proxies.map(proxy => 
        headers.map(header => {
          const value = proxy[header as keyof Proxy];
          return typeof value === 'string' ? `"${value}"` : value;
        }).join(',')
      )
    ].join('\n');

    return csvContent;
  };

  // 生成JSON內容
  const generateJSON = (proxies: Proxy[], includeMetadata: boolean) => {
    const data = proxies.map(proxy => {
      const { id, ...proxyData } = proxy;
      if (!includeMetadata) {
        delete proxyData.createdAt;
        delete proxyData.updatedAt;
        delete proxyData.lastChecked;
      }
      return proxyData;
    });

    return JSON.stringify({
      exportDate: new Date().toISOString(),
      totalCount: proxies.length,
      proxies: data
    }, null, 2);
  };

  // 生成TXT內容
  const generateTXT = (proxies: Proxy[]) => {
    return proxies.map(proxy => `${proxy.host}:${proxy.port}`).join('\n');
  };

  // 生成XML內容
  const generateXML = (proxies: Proxy[], includeMetadata: boolean) => {
    const metadata = includeMetadata ? ' includeMetadata="true"' : '';
    const proxyElements = proxies.map(proxy => {
      const elements = [
        `    <host>${proxy.host}</host>`,
        `    <port>${proxy.port}</port>`,
        `    <protocol>${proxy.protocol}</protocol>`,
        `    <status>${proxy.status}</status>`,
        `    <country>${proxy.country || ''}</country>`,
        `    <city>${proxy.city || ''}</city>`,
        `    <responseTime>${proxy.responseTime || 0}</responseTime>`,
        `    <anonymity>${proxy.anonymity || ''}</anonymity>`
      ];

      if (includeMetadata) {
        elements.push(`    <createdAt>${proxy.createdAt}</createdAt>`);
        elements.push(`    <updatedAt>${proxy.updatedAt}</updatedAt>`);
        elements.push(`    <lastChecked>${proxy.lastChecked}</lastChecked>`);
      }

      return `  <proxy>\n${elements.join('\n')}\n  </proxy>`;
    }).join('\n');

    return `<?xml version="1.0" encoding="UTF-8"?>
<proxies${metadata}>
  <exportDate>${new Date().toISOString()}</exportDate>
  <totalCount>${proxies.length}</totalCount>
${proxyElements}
</proxies>`;
  };

  // 下載文件
  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // 文件上傳配置
  const uploadProps: UploadProps = {
    name: 'file',
    accept: '.csv,.json,.txt,.xml',
    showUploadList: false,
    beforeUpload: (file) => {
      const isValidType = ['text/csv', 'application/json', 'text/plain', 'application/xml', 'text/xml'].includes(file.type) ||
                         ['.csv', '.json', '.txt', '.xml'].some(ext => file.name.toLowerCase().endsWith(ext));
      
      if (!isValidType) {
        message.error(t('proxy.invalidFileType'));
        return false;
      }

      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        message.error(t('proxy.fileTooLarge'));
        return false;
      }

      return true;
    },
    onChange: (info) => {
      if (info.file.status === 'uploading') {
        setImporting(true);
        setImportProgress(0);
      } else if (info.file.status === 'done') {
        setImportProgress(100);
        setTimeout(() => {
          setImporting(false);
          setImportProgress(0);
          setImportModalVisible(false);
        }, 1000);
      } else if (info.file.status === 'error') {
        setImporting(false);
        setImportProgress(0);
        message.error(t('proxy.importError'));
      }
    },
    customRequest: async ({ file, onSuccess, onError }) => {
      try {
        setImportProgress(20);
        
        const fileObj = file as File;
        const content = await fileObj.text();
        setImportProgress(50);
        
        const proxies = parseFileContent(content, fileObj.name);
        setImportProgress(80);
        
        onImport(proxies);
        setImportProgress(100);
        
        onSuccess?.(proxies);
        message.success(t('proxy.importSuccess', { count: proxies.length }));
      } catch (error) {
        onError?.(error as Error);
        message.error(t('proxy.importError'));
      }
    }
  };

  // 解析文件內容
  const parseFileContent = (content: string, filename: string): Proxy[] => {
    const extension = filename.toLowerCase().split('.').pop();
    
    switch (extension) {
      case 'csv':
        return parseCSV(content);
      case 'json':
        return parseJSON(content);
      case 'txt':
        return parseTXT(content);
      case 'xml':
        return parseXML(content);
      default:
        throw new Error(t('proxy.unsupportedFormat'));
    }
  };

  // 解析CSV
  const parseCSV = (content: string): Proxy[] => {
    const lines = content.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.replace(/"/g, '').trim());
    
    return lines.slice(1).map((line, index) => {
      const values = line.split(',').map(v => v.replace(/"/g, '').trim());
      const proxy: any = { id: `imported_${Date.now()}_${index}` };
      
      headers.forEach((header, i) => {
        proxy[header] = values[i] || '';
      });
      
      // 確保必要字段
      proxy.protocol = proxy.protocol || 'http';
      proxy.status = proxy.status || 'untested';
      proxy.createdAt = new Date();
      proxy.updatedAt = new Date();
      proxy.lastChecked = new Date();
      
      return proxy as Proxy;
    });
  };

  // 解析JSON
  const parseJSON = (content: string): Proxy[] => {
    const data = JSON.parse(content);
    const proxies = Array.isArray(data) ? data : data.proxies || [];
    
    return proxies.map((proxy: any, index: number) => ({
      id: proxy.id || `imported_${Date.now()}_${index}`,
      host: proxy.host,
      port: parseInt(proxy.port),
      protocol: proxy.protocol || 'http',
      status: proxy.status || 'untested',
      country: proxy.country || '',
      city: proxy.city || '',
      responseTime: proxy.responseTime || 0,
      anonymity: proxy.anonymity || '',
      createdAt: proxy.createdAt ? new Date(proxy.createdAt) : new Date(),
      updatedAt: proxy.updatedAt ? new Date(proxy.updatedAt) : new Date(),
      lastChecked: proxy.lastChecked ? new Date(proxy.lastChecked) : new Date()
    }));
  };

  // 解析TXT
  const parseTXT = (content: string): Proxy[] => {
    const lines = content.trim().split('\n');
    
    return lines.map((line, index) => {
      const [host, port] = line.trim().split(':');
      return {
        id: `imported_${Date.now()}_${index}`,
        host: host?.trim() || '',
        port: parseInt(port?.trim() || '8080'),
        protocol: 'http' as any,
        status: 'untested' as any,
        country: '',
        city: '',
        responseTime: 0,
        anonymity: '',
        createdAt: new Date(),
        updatedAt: new Date(),
        lastChecked: new Date()
      };
    });
  };

  // 解析XML
  const parseXML = (content: string): Proxy[] => {
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(content, 'text/xml');
    const proxyElements = xmlDoc.getElementsByTagName('proxy');
    
    return Array.from(proxyElements).map((element, index) => {
      const getTextContent = (tagName: string) => 
        element.getElementsByTagName(tagName)[0]?.textContent || '';
      
      return {
        id: `imported_${Date.now()}_${index}`,
        host: getTextContent('host'),
        port: parseInt(getTextContent('port') || '8080'),
        protocol: (getTextContent('protocol') || 'http') as ProxyProtocol,
        status: (getTextContent('status') || 'untested') as ProxyStatus,
        country: getTextContent('country'),
        city: getTextContent('city'),
        responseTime: parseInt(getTextContent('responseTime') || '0'),
        anonymity: getTextContent('anonymity'),
        createdAt: new Date(),
        updatedAt: new Date(),
        lastChecked: new Date()
      };
    });
  };

  return (
    <>
      <Space>
        <Button
          icon={<ExportOutlined />}
          onClick={() => setExportModalVisible(true)}
          loading={loading}
        >
          {t('proxy.exportProxies')}
        </Button>
        
        <Button
          icon={<ImportOutlined />}
          onClick={() => setImportModalVisible(true)}
          loading={loading}
        >
          {t('proxy.importProxies')}
        </Button>
      </Space>

      {/* 導出模態框 */}
      <Modal
        title={t('proxy.exportProxies')}
        open={exportModalVisible}
        onCancel={() => {
          setExportModalVisible(false);
          exportForm.resetFields();
        }}
        footer={null}
        width={500}
      >
        <Form
          form={exportForm}
          layout="vertical"
          onFinish={handleExport}
          initialValues={{
            format: 'csv',
            filter: 'all',
            includeMetadata: true
          }}
        >
          <Form.Item
            label={t('proxy.exportFormat')}
            name="format"
            rules={[{ required: true, message: t('validation.required') }]}
          >
            <Select>
              {exportConfig.formats.map(format => (
                <Option key={format.value} value={format.value}>
                  {format.label} - {format.description}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label={t('proxy.exportFilter')}
            name="filter"
            rules={[{ required: true, message: t('validation.required') }]}
          >
            <Select>
              {exportConfig.filters.map(filter => (
                <Option key={filter.value} value={filter.value}>
                  {filter.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label={t('proxy.includeMetadata')}
            name="includeMetadata"
            valuePropName="checked"
          >
            <input type="checkbox" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setExportModalVisible(false)}>
                {t('common.cancel')}
              </Button>
              <Button type="primary" htmlType="submit">
                {t('proxy.export')}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 導入模態框 */}
      <Modal
        title={t('proxy.importProxies')}
        open={importModalVisible}
        onCancel={() => {
          setImportModalVisible(false);
          setImportProgress(0);
          setImporting(false);
        }}
        footer={null}
        width={500}
      >
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <Upload.Dragger {...uploadProps}>
            <p className="ant-upload-drag-icon">
              <UploadOutlined />
            </p>
            <p className="ant-upload-text">{t('proxy.dragFileHere')}</p>
            <p className="ant-upload-hint">
              {t('proxy.supportedFormats')}: CSV, JSON, TXT, XML
            </p>
          </Upload.Dragger>

          {importing && (
            <div style={{ marginTop: 20 }}>
              <Progress percent={importProgress} status="active" />
              <p>{t('proxy.importing')}...</p>
            </div>
          )}
        </div>
      </Modal>
    </>
  );
};

export default FileOperations;
