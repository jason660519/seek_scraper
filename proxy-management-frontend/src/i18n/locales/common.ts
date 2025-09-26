/**
 * 通用翻譯配置
 * @author TRAE
 * @description 通用組件和操作的翻譯
 */

/**
 * 通用翻譯配置
 * @author TRAE
 * @description 通用組件和操作的翻譯
 */

const commonTranslations = {
  'zh-TW': {
    translation: {
      common: {
        confirm: '確認',
        cancel: '取消',
        save: '保存',
        delete: '刪除',
        edit: '編輯',
        add: '新增',
        search: '搜尋',
        reset: '重置',
        loading: '載入中...',
        noData: '暫無數據',
        error: '錯誤',
        success: '成功',
        warning: '警告',
        info: '資訊',
        yes: '是',
        no: '否',
        close: '關閉',
        refresh: '刷新',
        export: '導出',
        import: '導入',
        settings: '設置',
        logout: '登出',
        profile: '個人資料',
        language: '語言',
        theme: '主題',
        about: '關於',
        help: '幫助',
        autoRefresh: '自動刷新',
        totalItems: '共 {{total}} 項',
        details: '詳情',
        status: '狀態'
      },
      
      navigation: {
        dashboard: '儀表板',
        proxyManagement: '代理管理',
        systemMonitor: '系統監控',
        configuration: '配置中心',
        logs: '日誌查看',
        statistics: '統計分析',
        settings: '系統設置'
      },
      
      validation: {
        required: '此欄位為必填項',
        invalidFormat: '格式無效',
        invalidEmail: '郵箱格式無效',
        invalidUrl: 'URL格式無效',
        invalidNumber: '請輸入有效的數字',
        invalidPort: '端口必須在1-65535之間',
        minLength: '最少需要 {{count}} 個字符',
        maxLength: '最多允許 {{count}} 個字符',
        passwordMismatch: '密碼不匹配',
        fieldRequired: '請填寫此欄位'
      },
      
      error: {
        networkError: '網絡錯誤，請檢查網絡連接',
        serverError: '服務器錯誤，請稍後重試',
        unauthorized: '未授權，請重新登入',
        forbidden: '沒有權限執行此操作',
        notFound: '請求的資源不存在',
        validationError: '驗證失敗，請檢查輸入',
        unknownError: '未知錯誤，請聯繫管理員'
      }
    }
  },
  'zh-CN': {
    translation: {
      common: {
        confirm: '确认',
        cancel: '取消',
        save: '保存',
        delete: '删除',
        edit: '编辑',
        add: '新增',
        search: '搜索',
        reset: '重置',
        loading: '加载中...',
        noData: '暂无数据',
        error: '错误',
        success: '成功',
        warning: '警告',
        info: '信息',
        yes: '是',
        no: '否',
        close: '关闭',
        refresh: '刷新',
        export: '导出',
        import: '导入',
        settings: '设置',
        logout: '登出',
        profile: '个人资料',
        language: '语言',
        theme: '主题',
        about: '关于',
        help: '帮助',
        autoRefresh: '自动刷新',
        totalItems: '共 {{total}} 项',
        details: '详情',
        status: '状态'
      },
      
      navigation: {
        dashboard: '仪表板',
        proxyManagement: '代理管理',
        systemMonitor: '系统监控',
        configuration: '配置中心',
        logs: '日志查看',
        statistics: '统计分析',
        settings: '系统设置'
      },
      
      validation: {
        required: '此字段为必填项',
        invalidFormat: '格式无效',
        invalidEmail: '邮箱格式无效',
        invalidUrl: 'URL格式无效',
        invalidNumber: '请输入有效的数字',
        invalidPort: '端口必须在1-65535之间',
        minLength: '最少需要 {{count}} 个字符',
        maxLength: '最多允许 {{count}} 个字符',
        passwordMismatch: '密码不匹配',
        fieldRequired: '请填写此字段'
      },
      
      error: {
        networkError: '网络错误，请检查网络连接',
        serverError: '服务器错误，请稍后重试',
        unauthorized: '未授权，请重新登录',
        forbidden: '没有权限执行此操作',
        notFound: '请求的资源不存在',
        validationError: '验证失败，请检查输入',
        unknownError: '未知错误，请联系管理员'
      }
    }
  },
  'en': {
    translation: {
      common: {
        confirm: 'Confirm',
        cancel: 'Cancel',
        save: 'Save',
        delete: 'Delete',
        edit: 'Edit',
        add: 'Add',
        search: 'Search',
        reset: 'Reset',
        loading: 'Loading...',
        noData: 'No Data',
        error: 'Error',
        success: 'Success',
        warning: 'Warning',
        info: 'Info',
        yes: 'Yes',
        no: 'No',
        close: 'Close',
        refresh: 'Refresh',
        export: 'Export',
        import: 'Import',
        settings: 'Settings',
        logout: 'Logout',
        profile: 'Profile',
        language: 'Language',
        theme: 'Theme',
        about: 'About',
        help: 'Help',
        autoRefresh: 'Auto Refresh',
        totalItems: 'Total {{total}} items',
        details: 'Details',
        status: 'Status'
      },
      
      navigation: {
        dashboard: 'Dashboard',
        proxyManagement: 'Proxy Management',
        systemMonitor: 'System Monitor',
        configuration: 'Configuration',
        logs: 'Logs',
        statistics: 'Statistics',
        settings: 'Settings'
      },
      
      validation: {
        required: 'This field is required',
        invalidFormat: 'Invalid format',
        invalidEmail: 'Invalid email format',
        invalidUrl: 'Invalid URL format',
        invalidNumber: 'Please enter a valid number',
        invalidPort: 'Port must be between 1-65535',
        minLength: 'Minimum {{count}} characters required',
        maxLength: 'Maximum {{count}} characters allowed',
        passwordMismatch: 'Passwords do not match',
        fieldRequired: 'Please fill in this field'
      },
      
      error: {
        networkError: 'Network error, please check connection',
        serverError: 'Server error, please try again later',
        unauthorized: 'Unauthorized, please login again',
        forbidden: 'No permission to perform this action',
        notFound: 'Requested resource not found',
        validationError: 'Validation failed, please check input',
        unknownError: 'Unknown error, please contact administrator'
      }
    }
  }
};

export default commonTranslations;