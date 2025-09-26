/**
 * 主應用入口文件
 * @author TRAE
 * @description React 應用的入口點
 */

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

/**
 * 創建 React 根節點並渲染應用
 */
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
