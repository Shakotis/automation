# Google OAuth Publishing Requirements - Legal Pages

This document outlines the Privacy Policy and Terms of Service pages created to meet Google OAuth publishing requirements.

## Overview

For Google OAuth verification and publishing, Google requires:
1. A publicly accessible Privacy Policy
2. A publicly accessible Terms of Service
3. Proper disclosure of Google API usage and data handling

## Created Files

### 1. Privacy Policy (`/app/privacy/page.tsx`)
**URL:** `/privacy`

Comprehensive privacy policy that includes:
- **Information Collection:** Details about what data we collect and how
- **Google API Services User Data Policy Compliance:** Specific section addressing Google's requirements
- **Limited Use Disclosure:** Required statement for Google API Services
- **Google OAuth Scopes:** Clear explanation of requested permissions
- **Data Security:** Encryption and security measures
- **Data Sharing:** Transparency about third-party data sharing
- **Data Retention:** How long data is stored
- **User Rights:** GDPR and user data rights
- **Children's Privacy:** Protection for users under 18
- **Contact Information:** How to reach us

**Key Google OAuth Requirements Met:**
- ✅ Limited Use disclosure statement
- ✅ Detailed explanation of Google API scopes
- ✅ Transparency about data usage
- ✅ User rights and consent
- ✅ Data security measures

### 2. Terms of Service (`/app/terms/page.tsx`)
**URL:** `/terms`

Comprehensive terms of service that includes:
- **Service Description:** What Homework Scraper does
- **Account Requirements:** User obligations and security
- **Acceptable Use:** Permitted and prohibited activities
- **Google API Services:** Link to Google's policies
- **Intellectual Property:** Rights and ownership
- **Service Availability:** No guarantees and dependencies
- **Disclaimers:** Warranty disclaimers and liability limitations
- **Termination:** Account deletion and termination policies
- **Dispute Resolution:** Governing law and jurisdiction
- **Contact Information:** How to reach us

**Key Google OAuth Requirements Met:**
- ✅ Links to Google's Privacy Policy and Terms
- ✅ Clear description of service functionality
- ✅ User consent and authorization
- ✅ Compliance with third-party terms

### 3. Footer with Legal Links (`/app/layout.tsx`)
Added a site-wide footer with links to:
- Privacy Policy
- Terms of Service
- GitHub Repository

### 4. Updated Site Configuration (`/config/site.ts`)
Added `privacy` and `terms` links to the site configuration for easy reference throughout the app.

## Google OAuth Verification Checklist

When submitting your app for Google OAuth verification, ensure:

### Required URLs
- ✅ **Application Home Page:** Your main domain
- ✅ **Privacy Policy URL:** `https://yourdomain.com/privacy`
- ✅ **Terms of Service URL:** `https://yourdomain.com/terms`

### Scopes Being Requested
Our app requests:
1. `openid` - Authentication
2. `email` - User email address
3. `profile` - User profile information
4. `https://www.googleapis.com/auth/tasks` - Google Tasks access

### Limited Use Disclosure
The Privacy Policy includes the required Limited Use statement:
> "Homework Scraper's use and transfer to any other app of information received from Google APIs will adhere to Google API Services User Data Policy, including the Limited Use requirements."

### Data Usage Transparency
Both documents clearly explain:
- Why we need each scope
- How we use the data
- What data we store
- How long we keep it
- How users can revoke access

## Deployment Checklist

Before deploying to production:

1. **Update Contact Information:**
   - Replace `sadyvod19@gmail.com` with your official support email
   - Update GitHub links if needed

2. **Update Domain References:**
   - Search for "yourdomain.com" and replace with actual domain
   - Update GitHub repository links

3. **Review Legal Compliance:**
   - Consider having a lawyer review if handling sensitive data
   - Ensure compliance with local regulations (GDPR, COPPA, etc.)

4. **Make Pages Publicly Accessible:**
   - Privacy and Terms pages must be accessible without login
   - Verify they load correctly in production

5. **Add to Google OAuth Consent Screen:**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Navigate to APIs & Services > OAuth consent screen
   - Add Privacy Policy URL: `https://yourdomain.com/privacy`
   - Add Terms of Service URL: `https://yourdomain.com/terms`

## Verification Process

### 1. Initial OAuth Consent Screen Setup
- Application name: "Homework Scraper"
- User support email: Your email
- App domain: Your production domain
- Authorized domains: Add your domain
- Developer contact information: Your email

### 2. Scopes Configuration
Add the following scopes with justifications:
- `openid`, `email`, `profile`: "To authenticate users and create accounts"
- `https://www.googleapis.com/auth/tasks`: "To sync homework assignments to Google Tasks"

### 3. Test Users (During Development)
Add test user emails while in testing mode

### 4. Publishing Verification
When ready to publish:
1. Complete the OAuth consent screen information
2. Add Privacy Policy and Terms of Service URLs
3. Provide detailed scope justifications
4. Submit for verification
5. Wait for Google review (can take several days to weeks)

## Important Notes

### For Educational Apps
Since this app is designed for students (potentially under 18):
- The Privacy Policy includes a Children's Privacy section
- Minors should have parental consent
- Additional scrutiny may apply during Google review

### Limited Use Policy
Google has strict requirements for apps using sensitive/restricted scopes:
- Only use data for purposes explicitly disclosed
- Don't transfer data to third parties without disclosure
- Don't use data for advertising
- Don't allow humans to read data unless specific conditions met

### Data Retention
- Clearly state retention periods
- Allow users to delete their data
- Implement data deletion within stated timeframe (30 days)

## Testing the Pages

To test the pages locally:

```bash
cd frontend
npm run dev
```

Then visit:
- http://localhost:3000/privacy
- http://localhost:3000/terms

Verify:
- All links work correctly
- Content is readable and properly formatted
- Footer appears on all pages
- Mobile responsive layout works

## Maintenance

### Updating Policies
When updating Privacy Policy or Terms:
1. Update the "Last Updated" date
2. Notify users via email if changes are material
3. Consider keeping a changelog or version history
4. Keep previous versions archived for legal compliance

### Annual Review
Review and update these documents at least annually to:
- Reflect current practices
- Comply with new regulations
- Update contact information
- Add new features or data usage

## Additional Resources

- [Google API Services User Data Policy](https://developers.google.com/terms/api-services-user-data-policy)
- [OAuth 2.0 Policies](https://support.google.com/cloud/answer/9110914)
- [Google OAuth Verification Requirements](https://support.google.com/cloud/answer/9110914)
- [GDPR Compliance Guide](https://gdpr.eu/)

## Support

For questions about these legal documents or Google OAuth verification:
- Email: sadyvod19@gmail.com
- GitHub Issues: [automation repository](https://github.com/Shakotis/automation)

---

**Last Updated:** November 2, 2025
