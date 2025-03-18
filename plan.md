# Project: CSC2218 Note-Taking App Development Plan (Flet + Firebase)

---

## 1. Environment Setup (Week 1)  

**Objective:** Establish foundation for collaborative development  

### Tasks  

- **Git Configuration**  
  - Create private GitLab repo: “CSC2218 Group 4 Project 2025”  
  - Set up `.gitignore` for Python/Flet project  
  - Initialize `README.md` with project overview  

- **Development Environment**  
  - Install Python 3.11+  
  - Set up virtual environment:  

    ```bash
    python -m venv env
    source env/bin/activate  # Linux/Mac
    env\Scripts\activate  # Windows
    ```

  - Install essential libraries:  

    ```bash
    pip install flet firebase-admin requests pytest
    ```
  
- **IDE Setup**  
  - Install PyCharm or VS Code with Python/Flet plugins  
  - Configure Flet preview tools  
  - Set up GitLab integration plugin  
  
---

## 2. Component Development (Weeks 2-7)  

### **Week 2-3: Core Functionality**  

**Objective:** Implement basic CRUD operations  

### Tasks  

- **Database Module Development (Firebase)**  
  - Firestore schema design for notes  
  - CRUD operations in `firebase_db.py`  
  - Note model implementation (`n0tes3.py`)  

- **Basic UI (Flet)**  
  - Main screen with `ListView` for notes  
  - Note creation/edit dialog layout  
  - Floating Action Button for note creation  

#### **Week 4-5: Advanced Features**  

**Objective:** Implement mandatory complex features  

##### Tasks  

- **Social Sharing System**  
  - Android share intent integration  
  - Python text formatting utilities  

- **Tagging System**  
  - Flet `Chips` UI component for tags  
  - Firestore tag relationship implementation  

- **Firebase Cloud Storage Integration**  
  - User authentication (Firebase Auth)  
  - Image/file attachment support for notes  

#### **Week 6-7: Extension Features**  

**Objective:** Add 2+ unique value propositions  

##### Tasks  

- **Reminder System**  
  - Flet notification scheduling  
  - Python `datetime` utilities  
  
- **Label/Filter System**  
  - Multi-label Firestore architecture  
  - Filterable `ListView` adapter  

---

## 3. Testing Strategy (Parallel Development)  

**Objective:** Ensure reliability and requirements compliance  

#### Test Schedule  

- Weekly `pytest` runs (Python logic)  
- Bi-weekly UI validation using Flet unit tests  
- Final Week: Full test suite execution  

#### Test Types & Tools  

| Test Type       | Tools              | Coverage                      |
|----------------|-------------------|-------------------------------|
| Unit          | Pytest             | Database ops, Note model logic |
| Integration   | Flet Unit Tests    | UI workflow validation        |
| Performance   | Memory Profiler    | Memory/CPU usage monitoring   |
| Device Testing | Firebase Test Lab | Cross-device compatibility    |

---

## 4. Documentation & Compliance (Week 8)  

**Objective:** Prepare for submission/deployment  

#### Tasks  

- **UML Diagram Creation**  
  - Class diagrams (PlantUML)  
  - Sequence diagrams for key workflows  

- **Wiki Documentation**  
  - Architecture decisions log  
  - Testing plan summary  
  - Third-party library attributions  

---

## 5. Risk Management  

**Identified Risks:**  

1. Flet Firebase compatibility issues  
   *Mitigation:* Use REST API instead of Firebase SDK where needed  
2. Android permission handling for notifications  
   *Mitigation:* Ensure correct `AndroidManifest.xml` configuration  
3. Firestore quota limitations  
   *Mitigation:* Implement offline caching and error handling  

---

## 6. Team Collaboration Plan  

#### **Git Strategy:**  

- **Branching Model:**  
  - `main`: Production-ready code  
  - `dev`: Integration branch  
  - Feature branches: `feature/[name]`  

#### **Milestones:**  

1. Core CRUD (Week 3)  
2. Social Sharing (Week 5)  
3. Final Delivery (Week 8)  

#### **Code Reviews:**  

- Weekly merge requests with:  
  - Linting (Flake8) results  
  - Firebase security rule checks  
