# LinkedIn Developer App Setup Guide

This guide walks you through creating and configuring a LinkedIn Developer App for automated posting integration.

## Overview

To automate LinkedIn posting, you need to create a LinkedIn Developer Application that provides API access. This process involves several steps and requires approval from LinkedIn.

## Prerequisites

- **LinkedIn Account**: Personal or company LinkedIn account
- **Business Verification**: May be required for company page posting
- **Development Experience**: Basic understanding of OAuth and APIs

## Step 1: Access LinkedIn Developer Portal

1. **Go to LinkedIn Developer Portal**
   - Visit: https://developer.linkedin.com/
   - Click "Create App" or "My Apps"

2. **Sign In**
   - Use your LinkedIn credentials
   - Accept Developer Terms of Service if prompted

## Step 2: Create Your Application

### Basic App Information

1. **App Name**
   - Choose a descriptive name (e.g., "Content Calendar Automation")
   - Must be unique across LinkedIn

2. **LinkedIn Page**
   - **For Personal Apps**: Select your personal LinkedIn profile
   - **For Company Apps**: Select your company's LinkedIn page
   - Note: You must be an admin of the page to create apps for it

3. **App Logo**
   - Upload a square image (minimum 100x100px)
   - Represents your app in LinkedIn's system

4. **Legal Agreement**
   - Read and accept LinkedIn API Terms of Use
   - Review Privacy Policy requirements

### App Configuration

5. **App Description**
   ```
   Content calendar automation tool for scheduling and posting LinkedIn content. 
   Integrates with Google Sheets to automate social media posting workflows 
   for marketing teams and content creators.
   ```

6. **Website URL**
   - Your company/project website
   - Must be a valid, accessible URL

7. **Business Email**
   - Contact email for LinkedIn to reach you
   - Should be a professional email address

## Step 3: Configure App Products

### Add Required Products

1. **Navigate to Products Tab**
   - Click "Products" in your app dashboard

2. **Add "Share on LinkedIn" Product**
   - Click "Request Access" next to "Share on LinkedIn"
   - This enables posting capabilities
   - Usually approved instantly

3. **Add "Sign In with LinkedIn" Product**
   - Required for user authentication
   - Click "Request Access"
   - Usually approved instantly

### Advanced Products (If Needed)

4. **Marketing Developer Platform** (Optional)
   - Required for advanced analytics
   - Requires application and approval
   - Not needed for basic posting

5. **Community Management API** (For Organizations)
   - Required for posting as company pages
   - Requires detailed application
   - Review process can take several weeks

## Step 4: Configure Authentication

### OAuth 2.0 Settings

1. **Navigate to Auth Tab**
   - Click "Auth" in your app dashboard

2. **Add Authorized Redirect URLs**
   ```
   # For n8n (adjust port if different)
   http://localhost:5678/rest/oauth2-credential/callback
   
   # For production (use your domain)
   https://your-domain.com/oauth/callback
   
   # For n8n Cloud
   https://app.n8n.cloud/rest/oauth2-credential/callback
   ```

3. **Note Your Credentials**
   - **Client ID**: Copy this value
   - **Client Secret**: Copy this value (keep secure!)
   - **Primary Client Secret**: Use this for API calls

### Scope Configuration

4. **Default Scopes** (Automatically granted)
   - `r_liteprofile`: Basic profile information
   - `r_emailaddress`: Email address access

5. **Additional Scopes** (Request if needed)
   - `w_member_social`: Post on behalf of authenticated user
   - `r_organization_social`: Read organization posts
   - `w_organization_social`: Post as organization

## Step 5: Testing Your App

### Test Authentication Flow

1. **Create Test OAuth URL**
   ```
   https://www.linkedin.com/oauth/v2/authorization?
   response_type=code&
   client_id=YOUR_CLIENT_ID&
   redirect_uri=YOUR_REDIRECT_URI&
   scope=r_liteprofile%20w_member_social
   ```

2. **Test in Browser**
   - Paste URL in browser
   - Complete authorization flow
   - Verify redirect works correctly

### Verify API Access

3. **Test API Call** (using curl or Postman)
   ```bash
   curl -X GET \
     'https://api.linkedin.com/v2/people/~' \
     -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
   ```

## Step 6: Production Considerations

### App Review Process

1. **Basic Apps** (Personal posting)
   - Usually approved automatically
   - Can start using immediately

2. **Organization Apps** (Company posting)
   - Requires manual review
   - Submit detailed use case description
   - May take 2-4 weeks for approval

### Review Requirements

3. **Application Details**
   - Detailed description of use case
   - Screenshots of your application
   - Privacy policy URL
   - Terms of service URL

4. **Use Case Documentation**
   ```
   Our application automates content posting for marketing teams using 
   a Google Sheets-based content calendar. Users authenticate once and 
   can schedule posts to be automatically published at specified times. 
   
   This improves content consistency and saves manual posting time for 
   social media managers.
   ```

## Step 7: Integration with n8n

### Configure n8n Credentials

1. **Add LinkedIn Credential in n8n**
   - Go to Settings → Credentials
   - Add "LinkedIn OAuth2 API"
   - Enter your Client ID and Client Secret

2. **Test Connection**
   - Create test workflow
   - Add LinkedIn node
   - Authenticate and verify connection

### Webhook Configuration

3. **For Webhook Triggers** (Optional)
   ```
   Webhook URL: https://your-n8n-instance.com/webhook/linkedin
   HTTP Method: POST
   Authentication: Bearer token or API key
   ```

## Troubleshooting Common Issues

### Authentication Errors

**"Invalid client_id"**
- Verify Client ID is correct
- Check that app is properly created
- Ensure app is not suspended

**"Invalid redirect_uri"**
- Verify redirect URI exactly matches configured value
- Check for trailing slashes or typos
- Ensure URI is URL-encoded if needed

**"Invalid scope"**
- Ensure requested scopes are approved for your app
- Check that you're not requesting organization scopes without approval
- Verify scope names are spelled correctly

### API Access Issues

**"Forbidden" or 403 Errors**
- Check that required products are added to your app
- Verify your app has necessary permissions
- Ensure access tokens are not expired

**"Rate limit exceeded"**
- Implement exponential backoff
- Reduce request frequency
- Consider caching responses

### Approval Delays

**Community Management API**
- Response can take 2-4 weeks
- Provide detailed use case information
- Include mockups or screenshots
- Be specific about data usage

## Security Best Practices

### Credential Management

1. **Secure Storage**
   - Never commit client secrets to version control
   - Use environment variables or secure credential stores
   - Rotate secrets regularly

2. **Access Token Handling**
   - Store tokens securely
   - Implement token refresh logic
   - Use shortest practical token lifetime

### API Usage

3. **Rate Limiting**
   - Respect LinkedIn's rate limits
   - Implement retry logic with backoff
   - Monitor usage patterns

4. **Data Handling**
   - Follow GDPR and privacy regulations
   - Minimize data collection
   - Implement proper data retention policies

## API Limits and Quotas

### Free Tier Limits

- **API Calls**: 100 calls per day per user
- **Posts**: Limited by user's natural posting limits
- **Rate Limits**: 500 calls per hour per app

### Commercial Use

- **Higher Limits**: Available through partner programs
- **Custom Quotas**: Negotiable for enterprise use
- **SLA Support**: Available for approved partners

## Support and Resources

### LinkedIn Resources

- **Developer Documentation**: https://docs.microsoft.com/en-us/linkedin/
- **API Reference**: https://docs.microsoft.com/en-us/linkedin/shared/references
- **Support Portal**: https://linkedin.help/

### Community Support

- **Stack Overflow**: Tag questions with `linkedin-api`
- **GitHub Discussions**: Many open-source projects available
- **Developer Forums**: LinkedIn maintains community forums

## Compliance and Legal

### Terms of Service

- Review LinkedIn API Terms of Use
- Ensure compliance with posting guidelines
- Respect user privacy and data handling requirements

### Privacy Policy

- Include LinkedIn data usage in your privacy policy
- Clearly state what data you collect and how it's used
- Provide opt-out mechanisms for users

### Rate Limiting

- Implement proper rate limiting
- Use exponential backoff for retries
- Monitor and log API usage

## Next Steps

After completing this setup:

1. **Test Your Integration**
   - Create test posts using the API
   - Verify authentication flow works
   - Test error handling scenarios

2. **Implement Your Workflow**
   - Set up n8n workflow using provided templates
   - Configure Google Sheets integration
   - Test end-to-end automation

3. **Monitor and Maintain**
   - Set up monitoring for API health
   - Implement logging for debugging
   - Plan for credential rotation

4. **Scale Considerations**
   - Monitor API usage against limits
   - Plan for increased volume
   - Consider upgrading to partner programs if needed

For implementation help, refer to the [n8n LinkedIn Automation Guide](./n8n-linkedin-automation.md).