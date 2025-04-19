# **🚀 Smart CoderabbitAI Review Bot**  
**Automated, Cost-Efficient Code Reviews **  

---

## **✨ Key Features**  

✅ **Smart PR Filtering**  
- Automatically skips **draft PRs** (no wasted reviews)  
- Ignores **internal same-repo PRs** (further cost savings)  

✅ **Duplicate Prevention**  
- Checks for existing review requests before commenting  
- Prevents duplicate billing from multiple triggers  

✅ **Review Tracking**  
- Auto-adds `coderabbit-review-requested` label  
- Clear visibility into pending reviews  
---

## **🛠️ Technical Implementation**  

### **1. Trigger Logic**  
```yaml
on:
  pull_request:
    types: [opened, reopened, ready_for_review]  # Triggers on key PR events
```

### **2. Smart Filtering System**  
```yaml
- name: Check for draft PR
  if: github.event.pull_request.draft == true  # Skip draft PRs
  run: exit 0

- name: Check for internal PR
  if: github.event.pull_request.head.repo.full_name == github.event.pull_request.base.repo.full_name  # Skip internal PRs
  run: exit 0
```

### **3. Rate-Limited Review Trigger**  
```javascript
// Checks for existing bot comments
const hasExistingReview = comments.data.some(c => 
  c.user.login === 'coderabbitbot-testpress' && 
  c.body.includes('@coderabbitai review')
);

if (!hasExistingReview) {
  // Posts review request
  await github.rest.issues.createComment({
    issue_number: context.payload.pull_request.number,
    body: "@coderabbitai review"
  });
  
  // Adds tracking label
  await github.rest.issues.addLabels({
    issue_number: context.payload.pull_request.number,
    labels: ['coderabbit-review-requested']
  });
}
```

### **4. Permission Structure**  
```yaml
permissions:
  issues: write       # For comments/labels
  pull-requests: write # For PR access
  contents: read      # For file checking
```

---

## **📸 How It Works**  

### **1. Normal PR Flow**  
![image](https://github.com/user-attachments/assets/f5287a84-f955-4927-b229-97e3f782d1ef)
![image](https://github.com/user-attachments/assets/d7975ffb-8338-4780-ba8d-03bd69bfc475)

1. PR opened → Workflow triggers  
2. Bot checks for duplicates → None found  
3. Posts `@coderabbitai review` comment  
4. Adds `coderabbit-review-requested` label  

### **2. Filtered PR Flow**  
- **Draft PR** → Immediate exit (no action)  
- **Internal PR** → Immediate exit (no action)  
- **Duplicate** → Skips commenting (checks existing)  

---

## **⚡ Setup Guide**  

### **1. Prerequisites**  
- GitHub repo with GitHub Actions enabled  
- Bot account with `repo` scope permissions  

### **2. Installation**  
1. **Add bot token secret**:  
   - Create PAT with `repo` permissions  
   - Add as `Bot` secret in repo settings  

2. **Create workflow file**:  
   - Save as `.github/workflows/coderabbit-review.yml`  
   - Use the complete YAML from above  

---
