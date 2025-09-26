/**
 * 系統管理頁面翻譯配置
 * @author TRAE
 * @description 系統管理頁面的多語言支持
 */

/**
 * 系統管理頁面翻譯配置
 * @author TRAE
 * @description 系統管理頁面的多語言支持
 */

const systemTranslations = {
  'zh-TW': {
    translation: {
      system: {
        title: '系統管理',
        userManagement: '用戶管理',
        roleManagement: '角色管理',
        systemLogs: '系統日誌',
        systemConfig: '系統配置',
        backupRestore: '備份與恢復',
        
        user: {
          title: '用戶管理',
          username: '用戶名',
          email: '電子郵件',
          role: '角色',
          status: '狀態',
          createdAt: '創建時間',
          actions: '操作',
          addUser: '新增用戶',
          editUser: '編輯用戶'
        },
        
        userStatus: {
          active: '活躍',
          inactive: '非活躍',
          locked: '鎖定'
        },
        
        role: {
          title: '角色管理',
          name: '角色名稱',
          description: '描述',
          permissions: '權限',
          createdAt: '創建時間',
          addRole: '新增角色',
          editRole: '編輯角色'
        },
        
        logs: {
          title: '系統日誌',
          level: '級別',
          message: '消息',
          timestamp: '時間戳',
          user: '用戶',
          action: '操作',
          target: '目標',
          details: '詳情'
        },
        
        logLevel: {
          info: '信息',
          warning: '警告',
          error: '錯誤',
          debug: '調試'
        },
        
        config: {
          title: '系統配置',
          general: '常規設置',
          security: '安全設置',
          performance: '性能設置',
          email: '郵件設置',
          saveConfig: '保存配置',
          resetConfig: '重置配置'
        }
      }
    }
  },
  'zh-CN': {
    translation: {
      system: {
        title: '系统管理',
        userManagement: '用户管理',
        roleManagement: '角色管理',
        systemLogs: '系统日志',
        systemConfig: '系统配置',
        backupRestore: '备份与恢复',
        
        user: {
          title: '用户管理',
          username: '用户名',
          email: '电子邮件',
          role: '角色',
          status: '状态',
          createdAt: '创建时间',
          actions: '操作',
          addUser: '新增用户',
          editUser: '编辑用户'
        },
        
        userStatus: {
          active: '活跃',
          inactive: '非活跃',
          locked: '锁定'
        },
        
        role: {
          title: '角色管理',
          name: '角色名称',
          description: '描述',
          permissions: '权限',
          createdAt: '创建时间',
          addRole: '新增角色',
          editRole: '编辑角色'
        },
        
        logs: {
          title: '系统日志',
          level: '级别',
          message: '消息',
          timestamp: '时间戳',
          user: '用户',
          action: '操作',
          target: '目标',
          details: '详情'
        },
        
        logLevel: {
          info: '信息',
          warning: '警告',
          error: '错误',
          debug: '调试'
        },
        
        config: {
          title: '系统配置',
          general: '常规设置',
          security: '安全设置',
          performance: '性能设置',
          email: '邮件设置',
          saveConfig: '保存配置',
          resetConfig: '重置配置'
        }
      }
    }
  },
  'en': {
    translation: {
      system: {
        title: 'System Management',
        userManagement: 'User Management',
        roleManagement: 'Role Management',
        systemLogs: 'System Logs',
        systemConfig: 'System Configuration',
        backupRestore: 'Backup & Restore',
        
        user: {
          title: 'User Management',
          username: 'Username',
          email: 'Email',
          role: 'Role',
          status: 'Status',
          createdAt: 'Created At',
          actions: 'Actions',
          addUser: 'Add User',
          editUser: 'Edit User'
        },
        
        userStatus: {
          active: 'Active',
          inactive: 'Inactive',
          locked: 'Locked'
        },
        
        role: {
          title: 'Role Management',
          name: 'Role Name',
          description: 'Description',
          permissions: 'Permissions',
          createdAt: 'Created At',
          addRole: 'Add Role',
          editRole: 'Edit Role'
        },
        
        logs: {
          title: 'System Logs',
          level: 'Level',
          message: 'Message',
          timestamp: 'Timestamp',
          user: 'User',
          action: 'Action',
          target: 'Target',
          details: 'Details'
        },
        
        logLevel: {
          info: 'Info',
          warning: 'Warning',
          error: 'Error',
          debug: 'Debug'
        },
        
        config: {
          title: 'System Configuration',
          general: 'General Settings',
          security: 'Security Settings',
          performance: 'Performance Settings',
          email: 'Email Settings',
          saveConfig: 'Save Config',
          resetConfig: 'Reset Config'
        }
      }
    }
  }
};

export default systemTranslations;