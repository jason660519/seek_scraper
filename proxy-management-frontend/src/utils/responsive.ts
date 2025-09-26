/**
 * 響應式設計工具
 * @author TRAE
 * @description 處理響應式佈局和斷點管理
 */

import { useState, useEffect } from 'react';

// 斷點定義
export const breakpoints = {
  xs: 0,
  sm: 576,
  md: 768,
  lg: 992,
  xl: 1200,
  xxl: 1600
} as const;

export type Breakpoint = keyof typeof breakpoints;

// 響應式配置
export const responsiveConfig = {
  // 網格系統
  grid: {
    xs: { span: 24, offset: 0 },
    sm: { span: 12, offset: 0 },
    md: { span: 8, offset: 0 },
    lg: { span: 6, offset: 0 },
    xl: { span: 4, offset: 0 }
  },
  
  // 間距系統
  spacing: {
    xs: 8,
    sm: 12,
    md: 16,
    lg: 20,
    xl: 24
  },
  
  // 字體大小
  fontSize: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 20
  },
  
  // 卡片間距
  cardPadding: {
    xs: 12,
    sm: 16,
    md: 20,
    lg: 24,
    xl: 32
  }
};

/**
 * 獲取當前斷點
 */
export const getCurrentBreakpoint = (width: number): Breakpoint => {
  if (width >= breakpoints.xxl) return 'xxl';
  if (width >= breakpoints.xl) return 'xl';
  if (width >= breakpoints.lg) return 'lg';
  if (width >= breakpoints.md) return 'md';
  if (width >= breakpoints.sm) return 'sm';
  return 'xs';
};

/**
 * 檢查是否為移動設備
 */
export const isMobile = (width: number): boolean => {
  return width < breakpoints.md;
};

/**
 * 檢查是否為平板設備
 */
export const isTablet = (width: number): boolean => {
  return width >= breakpoints.md && width < breakpoints.lg;
};

/**
 * 檢查是否為桌面設備
 */
export const isDesktop = (width: number): boolean => {
  return width >= breakpoints.lg;
};

/**
 * 響應式Hook
 */
export const useResponsive = () => {
  const [screenSize, setScreenSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 1200,
    height: typeof window !== 'undefined' ? window.innerHeight : 800
  });

  useEffect(() => {
    const handleResize = () => {
      setScreenSize({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const breakpoint = getCurrentBreakpoint(screenSize.width);
  const isMobileDevice = isMobile(screenSize.width);
  const isTabletDevice = isTablet(screenSize.width);
  const isDesktopDevice = isDesktop(screenSize.width);

  return {
    screenSize,
    breakpoint,
    isMobile: isMobileDevice,
    isTablet: isTabletDevice,
    isDesktop: isDesktopDevice,
    // 便捷方法
    getSpacing: (size: keyof typeof responsiveConfig.spacing = 'md') => 
      responsiveConfig.spacing[size],
    getFontSize: (size: keyof typeof responsiveConfig.fontSize = 'md') => 
      responsiveConfig.fontSize[size],
    getCardPadding: (size: keyof typeof responsiveConfig.cardPadding = 'md') => 
      responsiveConfig.cardPadding[size],
    getGridSpan: (size: keyof typeof responsiveConfig.grid = 'md') => 
      responsiveConfig.grid[size].span
  };
};

/**
 * 響應式列配置
 */
export const getResponsiveColumns = (breakpoint: Breakpoint) => {
  const config = {
    xs: 1,
    sm: 2,
    md: 3,
    lg: 4,
    xl: 6,
    xxl: 8
  };
  
  return config[breakpoint];
};

/**
 * 響應式表格配置
 */
export const getResponsiveTableConfig = (breakpoint: Breakpoint) => {
  const config = {
    xs: {
      scroll: { x: 800 },
      pagination: { pageSize: 5 },
      size: 'small' as const
    },
    sm: {
      scroll: { x: 1000 },
      pagination: { pageSize: 10 },
      size: 'small' as const
    },
    md: {
      scroll: { x: 1200 },
      pagination: { pageSize: 15 },
      size: 'middle' as const
    },
    lg: {
      scroll: { x: 1400 },
      pagination: { pageSize: 20 },
      size: 'middle' as const
    },
    xl: {
      scroll: { x: 1600 },
      pagination: { pageSize: 25 },
      size: 'large' as const
    },
    xxl: {
      scroll: { x: 1800 },
      pagination: { pageSize: 30 },
      size: 'large' as const
    }
  };
  
  return config[breakpoint];
};

/**
 * 響應式表單配置
 */
export const getResponsiveFormConfig = (breakpoint: Breakpoint) => {
  const config = {
    xs: {
      layout: 'vertical' as const,
      labelCol: { span: 24 },
      wrapperCol: { span: 24 }
    },
    sm: {
      layout: 'vertical' as const,
      labelCol: { span: 24 },
      wrapperCol: { span: 24 }
    },
    md: {
      layout: 'horizontal' as const,
      labelCol: { span: 8 },
      wrapperCol: { span: 16 }
    },
    lg: {
      layout: 'horizontal' as const,
      labelCol: { span: 6 },
      wrapperCol: { span: 18 }
    },
    xl: {
      layout: 'horizontal' as const,
      labelCol: { span: 4 },
      wrapperCol: { span: 20 }
    },
    xxl: {
      layout: 'horizontal' as const,
      labelCol: { span: 3 },
      wrapperCol: { span: 21 }
    }
  };
  
  return config[breakpoint];
};

/**
 * 響應式卡片配置
 */
export const getResponsiveCardConfig = (breakpoint: Breakpoint) => {
  const config = {
    xs: {
      bodyStyle: { padding: '12px' },
      headStyle: { padding: '8px 12px' }
    },
    sm: {
      bodyStyle: { padding: '16px' },
      headStyle: { padding: '12px 16px' }
    },
    md: {
      bodyStyle: { padding: '20px' },
      headStyle: { padding: '16px 20px' }
    },
    lg: {
      bodyStyle: { padding: '24px' },
      headStyle: { padding: '20px 24px' }
    },
    xl: {
      bodyStyle: { padding: '32px' },
      headStyle: { padding: '24px 32px' }
    },
    xxl: {
      bodyStyle: { padding: '40px' },
      headStyle: { padding: '32px 40px' }
    }
  };
  
  return config[breakpoint];
};

/**
 * 響應式導航配置
 */
export const getResponsiveNavConfig = (breakpoint: Breakpoint) => {
  const config = {
    xs: {
      mode: 'horizontal' as const,
      collapsed: true,
      width: 200
    },
    sm: {
      mode: 'horizontal' as const,
      collapsed: true,
      width: 200
    },
    md: {
      mode: 'inline' as const,
      collapsed: false,
      width: 200
    },
    lg: {
      mode: 'inline' as const,
      collapsed: false,
      width: 240
    },
    xl: {
      mode: 'inline' as const,
      collapsed: false,
      width: 280
    },
    xxl: {
      mode: 'inline' as const,
      collapsed: false,
      width: 320
    }
  };
  
  return config[breakpoint];
};

/**
 * 響應式圖表配置
 */
export const getResponsiveChartConfig = (breakpoint: Breakpoint) => {
  const config = {
    xs: {
      height: 200,
      fontSize: 10
    },
    sm: {
      height: 250,
      fontSize: 12
    },
    md: {
      height: 300,
      fontSize: 14
    },
    lg: {
      height: 350,
      fontSize: 16
    },
    xl: {
      height: 400,
      fontSize: 18
    },
    xxl: {
      height: 450,
      fontSize: 20
    }
  };
  
  return config[breakpoint];
};

export default {
  breakpoints,
  responsiveConfig,
  getCurrentBreakpoint,
  isMobile,
  isTablet,
  isDesktop,
  useResponsive,
  getResponsiveColumns,
  getResponsiveTableConfig,
  getResponsiveFormConfig,
  getResponsiveCardConfig,
  getResponsiveNavConfig,
  getResponsiveChartConfig
};
