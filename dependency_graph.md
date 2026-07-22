# Project Dependency & Concurrent Development Report

This report maps the module dependencies of the AI Governance & Compliance Copilot application and identifies independent development pathways to avoid merge conflicts.

---

## 1. Backend Dependency Graph

The following Mermaid diagram displays the import tree and dependency flows of the FastAPI backend application:

```mermaid
graph TD
    %% Base layers
    subgraph Models & Config
        ML_Risk[models/risk_level.py]
        CF_Settings[config/settings.py]
        CF_Logging[config/logging.py]
    end

    subgraph Validation Schemas
        SC_Analyze[schemas/analyze.py]
        SC_Compliance[schemas/compliance.py]
        SC_Report[schemas/report.py]
        SC_Common[schemas/common.py]
    end

    %% Services
    subgraph Compliance Core
        SR_Compliance[services/compliance_engine.py]
    end

    subgraph Prompt Analysis
        SR_PromptService[services/prompt_analysis_service.py]
        SR_PromptAnalyzer[services/prompt_analyzer/analyzer.py]
        SR_PromptDetectors[services/prompt_analyzer/detectors/*_detector.py]
        SR_PromptBase[services/prompt_analyzer/detectors/base.py]
    end

    subgraph Response Analysis
        SR_ResponseService[services/response_analysis_service.py]
        SR_ResponseAnalyzer[services/response_analyzer/analyzer.py]
        SR_ResponseDetectors[services/response_analyzer/detectors/*_detector.py]
        SR_ResponseBase[services/response_analyzer/detectors/base.py]
    end

    subgraph Report Core
        SR_ReportService[services/report_service.py]
    end

    %% Routing
    subgraph Routing Layer
        RT_Main[main.py]
        RT_Router[api/router.py]
        RT_Prompt[api/routes/analyze_prompt.py]
        RT_Response[api/routes/analyze_response.py]
        RT_Compliance[api/routes/compliance.py]
        RT_Report[api/routes/generate_report.py]
        RT_Health[api/routes/health.py]
    end

    %% Dependencies
    RT_Main --> CF_Settings
    RT_Main --> CF_Logging
    RT_Main --> RT_Router

    RT_Router --> RT_Prompt
    RT_Router --> RT_Response
    RT_Router --> RT_Compliance
    RT_Router --> RT_Report
    RT_Router --> RT_Health

    RT_Prompt --> SC_Analyze
    RT_Prompt --> SR_PromptService

    RT_Response --> SC_Analyze
    RT_Response --> SR_ResponseService

    RT_Compliance --> SC_Compliance
    RT_Compliance --> SR_Compliance

    RT_Report --> SC_Report
    RT_Report --> SR_ReportService

    SR_PromptService --> SR_PromptAnalyzer
    SR_PromptAnalyzer --> SR_PromptDetectors
    SR_PromptDetectors --> SR_PromptBase
    SR_PromptAnalyzer --> SC_Analyze
    SR_PromptAnalyzer --> ML_Risk

    SR_ResponseService --> SR_ResponseAnalyzer
    SR_ResponseAnalyzer --> SR_ResponseDetectors
    SR_ResponseDetectors --> SR_ResponseBase
    SR_ResponseAnalyzer --> SC_Analyze
    SR_ResponseAnalyzer --> ML_Risk

    SR_Compliance --> ML_Risk
    SR_Compliance --> SC_Compliance

    %% Compliance Detector depends on Compliance Engine
    SR_PromptDetectors -- "compliance_detector.py" --> SR_Compliance
    SR_ResponseDetectors -- "compliance_detector.py" --> SR_Compliance
```

---

## 2. Frontend Dependency Graph

The React frontend components are modular and decoupled:

```mermaid
graph TD
    Main[main.tsx] --> App[App.tsx]
    App --> Layout[components/layout/AppLayout.tsx]
    Layout --> Sidebar[components/layout/Sidebar.tsx]
    Layout --> TopBar[components/layout/TopBar.tsx]

    Sidebar --> Data[data/mockData.ts]

    %% Pages
    App --> Page_Dash[pages/DashboardPage.tsx]
    App --> Page_Prompt[pages/PromptAnalyzerPage.tsx]
    App --> Page_Response[pages/ResponseAnalyzerPage.tsx]
    App --> Page_Comp[pages/ComplianceEnginePage.tsx]
    App --> Page_Reports[pages/AuditReportsPage.tsx]
    App --> Page_Settings[pages/SettingsPage.tsx]

    %% UI Shared Elements
    Page_Dash --> UI_Panel[components/ui/Panel.tsx]
    Page_Dash --> UI_Badge[components/ui/Badge.tsx]
    Page_Dash --> UI_Prog[components/ui/ProgressBar.tsx]

    Page_Prompt --> UI_Workspace[components/analysis/AnalyzerWorkspace.tsx]
    Page_Response --> UI_Workspace
    UI_Workspace --> Lib_Analyzer[lib/analyzer.ts]

    Page_Comp --> UI_Panel
    Page_Comp --> UI_Badge
```

---

## 3. Parallel Development Pathways (Merge-Conflict Free)

To allow a multi-member team to deliver features rapidly without stepping on each other's code, we can structure development into **four independent pathways**:

### Pathway A: Individual Detectors (Plugin Strategy)
- **Work Area**: `backend/app/services/prompt_analyzer/detectors/` and `backend/app/services/response_analyzer/detectors/`
- **Why it is conflict-free**: Each detector is a separate file (e.g. `pii_detector.py`, `bias_detector.py`). A developer can add a new detector class or modify existing rules inside these files without affecting any others.
- **Architectural Recommendation**: Instead of importing and appending detectors manually in `analyzer.py`, implement dynamic package loading:
  ```python
  # Dynamic loading snippet for analyzer.py
  import pkgutil
  import importlib
  # Walk and load all sub-modules dynamically to prevent editing the analyzer.py registry
  ```

### Pathway B: Audit Report Compilation Engine
- **Work Area**: `backend/app/services/report_service.py` and `backend/app/schemas/report.py`
- **Why it is conflict-free**: This service compiles analytical outputs into formatted files (e.g., PDF generation using ReportLab, or CSV exports). It consumes schemas but operates entirely downstream from the real-time request analyzers.

### Pathway C: Database & Persistence Layer
- **Work Area**: Creating a new database module (e.g. `backend/app/db/` containing models, session managers, and Alembic migrations)
- **Why it is conflict-free**: Developing the database schema and queries is pure creation. The existing analyzers are stateless, meaning a developer can write repository classes to persist logs in the background without modifying the active code.

### Pathway D: Frontend UI Page Views
- **Work Area**: `frontend/src/pages/`
- **Why it is conflict-free**: The pages are standalone React components. Once the routing shell in `App.tsx` and `Sidebar.tsx` defines the URLs, developers can build the settings UI, dashboards, and reporting viewports in parallel.
