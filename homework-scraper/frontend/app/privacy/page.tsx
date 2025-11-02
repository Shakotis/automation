import { title } from "@/components/primitives";

export default function PrivacyPolicyPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className={title()}>Privacy Policy</h1>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-8">
        Last Updated: November 2, 2025
      </p>

      <div className="space-y-6 text-gray-800 dark:text-gray-200">
        <section>
          <h2 className="text-2xl font-bold mb-3">1. Introduction</h2>
          <p>
            Welcome to Homework Scraper ("we," "our," or "us"). We are committed to protecting your
            personal information and your right to privacy. This Privacy Policy explains how we
            collect, use, disclose, and safeguard your information when you use our application.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">2. Information We Collect</h2>
          
          <h3 className="text-xl font-semibold mb-2 mt-4">2.1 Information You Provide</h3>
          <ul className="list-disc pl-6 space-y-2">
            <li>
              <strong>Account Information:</strong> When you create an account, we collect your email
              address and any profile information you provide through Google OAuth.
            </li>
            <li>
              <strong>Educational Platform Credentials:</strong> We collect and encrypt credentials
              for Lithuanian educational platforms (TAMO, eVartai, Mano Dienynas) that you choose to
              connect to our service.
            </li>
            <li>
              <strong>User Preferences:</strong> Settings and preferences you configure within the
              application.
            </li>
          </ul>

          <h3 className="text-xl font-semibold mb-2 mt-4">2.2 Information Collected Automatically</h3>
          <ul className="list-disc pl-6 space-y-2">
            <li>
              <strong>Usage Data:</strong> Information about how you interact with our application,
              including features used and actions taken.
            </li>
            <li>
              <strong>Device Information:</strong> Information about the device you use to access our
              service, including IP address, browser type, and operating system.
            </li>
            <li>
              <strong>Log Data:</strong> Server logs that may include your IP address, access times,
              and pages viewed.
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">3. How We Use Your Information</h2>
          <p className="mb-2">We use the information we collect to:</p>
          <ul className="list-disc pl-6 space-y-2">
            <li>Provide, operate, and maintain our service</li>
            <li>Authenticate your identity and manage your account</li>
            <li>
              Scrape homework and exam information from educational platforms you've authorized
            </li>
            <li>Sync your homework data to Google Tasks (with your permission)</li>
            <li>Send you notifications about homework deadlines and updates</li>
            <li>Improve and optimize our service</li>
            <li>Respond to your inquiries and provide customer support</li>
            <li>Detect, prevent, and address technical issues and security threats</li>
            <li>Comply with legal obligations</li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">4. Google API Services User Data Policy</h2>
          <p className="mb-2">
            Our use of information received from Google APIs adheres to the{" "}
            <a
              href="https://developers.google.com/terms/api-services-user-data-policy"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline"
            >
              Google API Services User Data Policy
            </a>
            , including the Limited Use requirements.
          </p>
          
          <h3 className="text-xl font-semibold mb-2 mt-4">4.1 Google OAuth Scopes</h3>
          <p className="mb-2">We request the following Google OAuth scopes:</p>
          <ul className="list-disc pl-6 space-y-2">
            <li>
              <strong>openid, email, profile:</strong> To authenticate you and create your account
            </li>
            <li>
              <strong>https://www.googleapis.com/auth/tasks:</strong> To sync homework assignments to
              your Google Tasks (only if you grant permission)
            </li>
          </ul>

          <h3 className="text-xl font-semibold mb-2 mt-4">4.2 Limited Use Disclosure</h3>
          <p>
            Homework Scraper's use and transfer to any other app of information received from Google
            APIs will adhere to{" "}
            <a
              href="https://developers.google.com/terms/api-services-user-data-policy#additional_requirements_for_specific_api_scopes"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline"
            >
              Google API Services User Data Policy
            </a>
            , including the Limited Use requirements.
          </p>
          <p className="mt-2">
            We only use Google Tasks API to create and manage tasks based on your homework
            assignments. We do not read, modify, or delete any tasks not created by our service.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">5. Data Security</h2>
          <p className="mb-2">
            We implement appropriate technical and organizational security measures to protect your
            personal information:
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li>
              <strong>Encryption:</strong> Educational platform credentials are encrypted using
              industry-standard encryption (Fernet) before storage
            </li>
            <li>
              <strong>Secure Transmission:</strong> All data transmitted between your device and our
              servers uses HTTPS/TLS encryption
            </li>
            <li>
              <strong>Access Controls:</strong> Strict access controls limit who can access user data
            </li>
            <li>
              <strong>Regular Security Audits:</strong> We regularly review our security practices
            </li>
          </ul>
          <p className="mt-2">
            However, no method of transmission over the Internet or electronic storage is 100% secure.
            While we strive to use commercially acceptable means to protect your information, we cannot
            guarantee absolute security.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">6. Data Sharing and Disclosure</h2>
          <p className="mb-2">
            We do not sell, trade, or rent your personal information to third parties. We may share
            your information only in the following circumstances:
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li>
              <strong>With Your Consent:</strong> When you explicitly authorize us to share your
              information (e.g., syncing to Google Tasks)
            </li>
            <li>
              <strong>Service Providers:</strong> With trusted third-party service providers who assist
              us in operating our service (e.g., hosting providers), under strict confidentiality
              agreements
            </li>
            <li>
              <strong>Legal Requirements:</strong> When required by law, court order, or governmental
              authority
            </li>
            <li>
              <strong>Protection of Rights:</strong> To protect our rights, property, or safety, or
              that of our users or the public
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">7. Data Retention</h2>
          <p>
            We retain your personal information only as long as necessary to provide our services and
            fulfill the purposes outlined in this Privacy Policy. When you delete your account, we will
            delete or anonymize your personal information within 30 days, except where we are required
            to retain it for legal or regulatory purposes.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">8. Your Rights and Choices</h2>
          <p className="mb-2">You have the following rights regarding your personal information:</p>
          <ul className="list-disc pl-6 space-y-2">
            <li>
              <strong>Access:</strong> Request access to the personal information we hold about you
            </li>
            <li>
              <strong>Correction:</strong> Request correction of inaccurate or incomplete information
            </li>
            <li>
              <strong>Deletion:</strong> Request deletion of your personal information
            </li>
            <li>
              <strong>Opt-Out:</strong> Opt-out of certain data collection and processing activities
            </li>
            <li>
              <strong>Revoke Consent:</strong> Revoke Google OAuth permissions at any time through your
              Google Account settings or within our application settings
            </li>
            <li>
              <strong>Data Portability:</strong> Request a copy of your data in a portable format
            </li>
          </ul>
          <p className="mt-2">
            To exercise any of these rights, please contact us using the contact information provided
            below.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">9. Children's Privacy</h2>
          <p>
            Our service is intended for use by students and may be used by individuals under the age of
            18. If you are under 18, please ensure you have permission from a parent or guardian before
            using our service. We do not knowingly collect personal information from children under 13
            without parental consent. If we become aware that we have collected personal information
            from a child under 13 without parental consent, we will take steps to delete that
            information.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">10. International Data Transfers</h2>
          <p>
            Your information may be transferred to and processed in countries other than your country of
            residence. These countries may have different data protection laws. When we transfer your
            information, we ensure appropriate safeguards are in place to protect your data.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">11. Third-Party Links</h2>
          <p>
            Our service may contain links to third-party websites or services. We are not responsible
            for the privacy practices or content of these third parties. We encourage you to review the
            privacy policies of any third-party sites you visit.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">12. Changes to This Privacy Policy</h2>
          <p>
            We may update this Privacy Policy from time to time. We will notify you of any material
            changes by posting the new Privacy Policy on this page and updating the "Last Updated" date.
            Your continued use of our service after any changes constitutes your acceptance of the new
            Privacy Policy.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">13. Contact Us</h2>
          <p className="mb-2">
            If you have any questions, concerns, or requests regarding this Privacy Policy or our data
            practices, please contact us at:
          </p>
          <div className="pl-6">
            <p>
              <strong>Email:</strong> dovydasjusevicius@gmail.com
            </p>
            <p>
              <strong>GitHub:</strong>{" "}
              <a
                href="https://github.com/Shakotis/automation"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline"
              >
                https://github.com/Shakotis/automation
              </a>
            </p>
          </div>
        </section>

        <section className="mt-8 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
          <h2 className="text-2xl font-bold mb-3">GDPR Rights (For EU Users)</h2>
          <p className="mb-2">
            If you are located in the European Economic Area (EEA), you have additional rights under
            the General Data Protection Regulation (GDPR):
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li>The right to be informed about data collection and use</li>
            <li>The right to access your personal data</li>
            <li>The right to rectification of inaccurate data</li>
            <li>The right to erasure ("right to be forgotten")</li>
            <li>The right to restrict processing</li>
            <li>The right to data portability</li>
            <li>The right to object to processing</li>
            <li>Rights related to automated decision-making and profiling</li>
          </ul>
          <p className="mt-2">
            To exercise these rights, please contact us using the contact information provided above.
          </p>
        </section>
      </div>
    </div>
  );
}
