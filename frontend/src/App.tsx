import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from './components/layout/AppLayout'
import { AuditReportsPage } from './pages/AuditReportsPage'
import { DashboardPage } from './pages/DashboardPage'
import { PromptAnalyzerPage } from './pages/PromptAnalyzerPage'
import { ResponseAnalyzerPage } from './pages/ResponseAnalyzerPage'
import { ComplianceEnginePage } from './pages/ComplianceEnginePage'
import { SettingsPage } from './pages/SettingsPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/prompt-analyzer" element={<PromptAnalyzerPage />} />
          <Route path="/response-analyzer" element={<ResponseAnalyzerPage />} />
          <Route path="/compliance-engine" element={<ComplianceEnginePage />} />
          <Route path="/audit-reports" element={<AuditReportsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}


export default App
