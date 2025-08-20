# n8n LinkedIn Automation Setup Guide

This guide explains how to set up automated LinkedIn posting using n8n with your content calendar.

## Overview

The enhanced content calendar now includes automation tracking columns:
- **Post ID**: LinkedIn post identifier after publishing
- **Automation Status**: Current state (Pending → Queued → Processing → Posted → Failed → Skipped)
- **n8n Execution ID**: Reference to the n8n workflow execution for debugging

## Prerequisites

### 1. n8n Installation

**Option A: Self-Hosted (Recommended - FREE)**
```bash
# Using Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Using npm
npm install n8n -g
n8n start
```

**Option B: n8n Cloud**
- Sign up at https://n8n.cloud
- Starts at $20/month for 2,500 executions

### 2. LinkedIn Developer App

1. Go to [LinkedIn Developer Portal](https://developer.linkedin.com/)
2. Create a new app with these settings:
   - **App Type**: Company Page or Personal Profile
   - **Products**: Add "Share on LinkedIn" and "Sign In with LinkedIn"
   - **Authorized Redirect URLs**: Add your n8n webhook URL
3. Note your **Client ID** and **Client Secret**

### 3. Required Permissions

Your LinkedIn app needs these scopes:
- `r_liteprofile` - Basic profile info
- `w_member_social` - Post on behalf of user
- `r_organization_social` - Read organization posts (if posting as company)
- `w_organization_social` - Post as organization (if posting as company)

## n8n Workflow Setup

### Basic Workflow Structure

```
[Trigger] → [Google Sheets] → [Process Content] → [LinkedIn] → [Update Status]
```

### Step 1: Create New Workflow

1. Open n8n interface (typically http://localhost:5678)
2. Click "New Workflow"
3. Name it "LinkedIn Content Calendar Automation"

### Step 2: Add Trigger Node

**Schedule Trigger (Recommended)**
- Node: "Schedule Trigger"
- Settings:
  - **Trigger Interval**: Every 15 minutes
  - **Timezone**: Your local timezone

**Alternative: Webhook Trigger**
- Node: "Webhook"
- **HTTP Method**: POST
- **Path**: /linkedin-automation

### Step 3: Google Sheets Node (Read Calendar)

- Node: "Google Sheets"
- **Operation**: Read
- **Resource**: Sheet Data
- **Range**: `A:J` (all columns including automation columns)
- **Authentication**: Use service account or OAuth

**Filter Criteria** (use Function node):
```javascript
// Only process LinkedIn posts that are approved and not yet processed
return items.filter(item => {
  const row = item.json;
  return row.Platform === 'LinkedIn' && 
         row.Status === 'Approved' && 
         (row['Automation Status'] === 'Pending' || row['Automation Status'] === '');
});
```

### Step 4: Content Processing Node

**Function Node** for content preparation:
```javascript
// Prepare content for LinkedIn posting
const items = [];

for (const item of $input.all()) {
  const row = item.json;
  
  // Validate content
  if (!row['Post Content'] || row['Post Content'].length > 3000) {
    continue; // Skip invalid content
  }
  
  // Schedule check - only post if time has arrived
  const scheduledDateTime = new Date(`${row.Date} ${row.Time}`);
  const now = new Date();
  
  if (scheduledDateTime > now) {
    continue; // Not time yet
  }
  
  items.push({
    json: {
      content: row['Post Content'],
      scheduleTime: scheduledDateTime,
      rowIndex: item.json.$row_index,
      originalData: row
    }
  });
}

return items;
```

### Step 5: LinkedIn Node

- Node: "LinkedIn"
- **Operation**: Create Post
- **Resource**: Share
- **Authentication**: OAuth2 (use your LinkedIn app credentials)

**Post Configuration**:
- **Content**: `{{$json.content}}`
- **Visibility**: PUBLIC (or CONNECTIONS as needed)
- **Post As**: Choose Person or Organization

### Step 6: Update Status Node

**Google Sheets Node** (Update):
- **Operation**: Update
- **Range**: Use dynamic range based on row index
- **Values**: Update Automation Status and Post ID

**Function Node** for status update:
```javascript
// Prepare status update data
const items = [];

for (const item of $input.all()) {
  const linkedinResponse = item.json;
  const originalRow = $('Content Processing').first().json.originalData;
  
  items.push({
    json: {
      range: `I${originalRow.$row_index}:J${originalRow.$row_index}`, // Automation Status and n8n Execution ID columns
      values: [
        ['Posted', $workflow.id + '_' + $execution.id]
      ]
    }
  });
}

return items;
```

### Step 7: Error Handling

**Add Error Workflow**:
1. Create branches for success/failure paths
2. Update Automation Status to "Failed" on errors
3. Send notifications for failures

**Function Node** for error handling:
```javascript
// Handle posting errors
if ($execution.data.error) {
  return [{
    json: {
      range: `I${$('Content Processing').first().json.originalData.$row_index}`,
      values: [['Failed']]
    }
  }];
}
```

## Advanced Features

### 1. Content Enhancement with AI

Add **OpenAI Node** before LinkedIn posting:
```javascript
// Enhance content with AI
const prompt = `Improve this LinkedIn post for maximum engagement:
"${$json.content}"

Make it more engaging while keeping the core message. Add relevant hashtags.`;

return [{
  json: {
    prompt: prompt,
    originalContent: $json.content
  }
}];
```

### 2. Optimal Posting Times

**Function Node** for timing analysis:
```javascript
// Check if current time is optimal for posting
const now = new Date();
const hour = now.getHours();
const day = now.getDay();

// Best times: Weekdays 8-10am, 12-2pm, 5-6pm
const isOptimalTime = (day >= 1 && day <= 5) && 
  ((hour >= 8 && hour <= 10) || 
   (hour >= 12 && hour <= 14) || 
   (hour >= 17 && hour <= 18));

if (!isOptimalTime) {
  // Delay posting to next optimal time
  throw new Error('Delaying to optimal posting time');
}

return $input.all();
```

### 3. Analytics Integration

Add **HTTP Request Node** to fetch post analytics:
```javascript
// Fetch LinkedIn post metrics after 24 hours
const postId = $json.linkedinPostId;

return [{
  json: {
    method: 'GET',
    url: `https://api.linkedin.com/v2/socialActions/${postId}`,
    headers: {
      'Authorization': 'Bearer ' + $credentials.linkedin.accessToken
    }
  }
}];
```

## Testing Your Workflow

### 1. Test Mode Setup

1. Create a test row in your calendar:
   - **Platform**: LinkedIn
   - **Status**: Approved
   - **Post Content**: "Test post from n8n automation"
   - **Automation Status**: Pending

2. Run workflow manually
3. Check that status updates correctly

### 2. Debug Common Issues

**Authentication Errors**:
- Verify LinkedIn app permissions
- Check OAuth token expiration
- Ensure correct redirect URLs

**Google Sheets Errors**:
- Verify service account permissions
- Check sheet ID and range format
- Test API access independently

**Content Validation**:
- Check character limits (3000 for LinkedIn)
- Verify required fields are present
- Test with various content types

## Security Best Practices

### 1. Credential Management

- Use n8n's built-in credential system
- Never hardcode API keys
- Set up credential rotation schedule

### 2. Access Control

- Limit workflow execution permissions
- Use least-privilege principle
- Monitor execution logs

### 3. Data Privacy

- Ensure GDPR compliance
- Implement data retention policies
- Use secure connections (HTTPS)

## Monitoring and Maintenance

### 1. Workflow Monitoring

- Set up email notifications for failures
- Monitor execution frequency
- Track success/failure rates

### 2. Regular Maintenance

- Update LinkedIn API versions
- Refresh authentication tokens
- Review and optimize workflows

### 3. Performance Optimization

- Batch process multiple posts
- Implement rate limiting
- Cache frequently used data

## Troubleshooting

### Common Error Messages

**"Invalid scope"**
- Check LinkedIn app permissions
- Ensure all required scopes are approved

**"Rate limit exceeded"**
- Implement exponential backoff
- Reduce posting frequency
- Use batch operations

**"Authentication failed"**
- Refresh OAuth tokens
- Check app configuration
- Verify redirect URLs

### Debug Steps

1. Test each node individually
2. Check execution logs in n8n
3. Verify Google Sheets permissions
4. Test LinkedIn API access manually
5. Review workflow logic step by step

## Support and Resources

- [n8n Documentation](https://docs.n8n.io/)
- [LinkedIn API Documentation](https://docs.microsoft.com/en-us/linkedin/)
- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Content Calendar GitHub Issues](../../issues)

## Cost Considerations

### Self-Hosted n8n (Recommended)
- **Cost**: FREE (except server costs)
- **Executions**: Unlimited
- **Control**: Full control over data and workflows

### n8n Cloud
- **Starter**: $20/month (2,500 executions)
- **Pro**: $50/month (10,000 executions)
- **Enterprise**: Custom pricing

### Execution Estimates
- **Basic workflow**: 1 execution per post
- **With AI enhancement**: 2-3 executions per post
- **Daily posting (5 posts)**: ~150 executions/month
- **Recommended**: Self-hosted for regular use