import { title } from "@/components/primitives";

export default function TermsOfServicePage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className={title()}>Terms of Service</h1>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-8">
        Last Updated: November 2, 2025
      </p>

      <div className="space-y-6 text-gray-800 dark:text-gray-200">
        <section>
          <h2 className="text-2xl font-bold mb-3">1. Acceptance of Terms</h2>
          <p>
            By accessing or using Homework Scraper ("the Service"), you agree to be bound by these
            Terms of Service ("Terms"). If you do not agree to these Terms, you may not access or use
            the Service. These Terms constitute a legally binding agreement between you and Homework
            Scraper.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">2. Description of Service</h2>
          <p className="mb-2">
            Homework Scraper is a web application that provides the following services:
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li>
              Automated scraping of homework assignments from Lithuanian educational platforms (TAMO,
              eVartai, Mano Dienynas)
            </li>
            <li>Aggregation and display of homework assignments in a unified dashboard</li>
            <li>Optional synchronization of homework to Google Tasks</li>
            <li>Exam date tracking and management</li>
            <li>Notifications about upcoming homework deadlines</li>
          </ul>
          <p className="mt-2">
            We reserve the right to modify, suspend, or discontinue any aspect of the Service at any
            time, with or without notice.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">3. User Accounts and Registration</h2>
          
          <h3 className="text-xl font-semibold mb-2 mt-4">3.1 Account Creation</h3>
          <p>
            To use the Service, you must create an account by signing in with Google OAuth. By creating
            an account, you represent and warrant that:
          </p>
          <ul className="list-disc pl-6 space-y-2 mt-2">
            <li>All information you provide is accurate, current, and complete</li>
            <li>You will maintain and update your information to keep it accurate and current</li>
            <li>You are at least 13 years of age, or have parental/guardian consent if under 18</li>
            <li>
              You have the legal capacity to enter into these Terms in your jurisdiction
            </li>
          </ul>

          <h3 className="text-xl font-semibold mb-2 mt-4">3.2 Account Security</h3>
          <p>
            You are responsible for maintaining the confidentiality of your account credentials and for
            all activities that occur under your account. You agree to:
          </p>
          <ul className="list-disc pl-6 space-y-2 mt-2">
            <li>Immediately notify us of any unauthorized use of your account</li>
            <li>Ensure that you log out from your account at the end of each session</li>
            <li>Not share your account credentials with others</li>
          </ul>
          <p className="mt-2">
            We are not liable for any loss or damage arising from your failure to protect your account
            information.
          </p>

          <h3 className="text-xl font-semibold mb-2 mt-4">3.3 Educational Platform Credentials</h3>
          <p>
            By providing credentials for educational platforms (TAMO, eVartai, Mano Dienynas), you:
          </p>
          <ul className="list-disc pl-6 space-y-2 mt-2">
            <li>
              Represent that you are the authorized user of those accounts or have permission to access
              them
            </li>
            <li>Authorize us to access those platforms on your behalf to retrieve homework data</li>
            <li>
              Acknowledge that we encrypt and securely store these credentials as described in our
              Privacy Policy
            </li>
            <li>
              Agree that you are responsible for compliance with the terms of service of those
              educational platforms
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">4. Acceptable Use</h2>
          
          <h3 className="text-xl font-semibold mb-2 mt-4">4.1 Permitted Use</h3>
          <p>
            You may use the Service only for lawful purposes and in accordance with these Terms. You
            agree to use the Service only for personal, non-commercial purposes related to managing your
            educational assignments.
          </p>

          <h3 className="text-xl font-semibold mb-2 mt-4">4.2 Prohibited Activities</h3>
          <p className="mb-2">You agree NOT to:</p>
          <ul className="list-disc pl-6 space-y-2">
            <li>Use the Service for any illegal or unauthorized purpose</li>
            <li>Violate any applicable laws, regulations, or third-party rights</li>
            <li>
              Attempt to gain unauthorized access to any portion of the Service, other user accounts, or
              any systems or networks
            </li>
            <li>Interfere with or disrupt the Service or servers connected to the Service</li>
            <li>Use automated means to access the Service beyond what we explicitly provide</li>
            <li>
              Reverse engineer, decompile, or disassemble any part of the Service (except as permitted
              by law)
            </li>
            <li>Remove, obscure, or alter any legal notices displayed in or along with the Service</li>
            <li>Use the Service to transmit any malicious code, viruses, or harmful materials</li>
            <li>Impersonate any person or entity or misrepresent your affiliation with any entity</li>
            <li>
              Use the Service in any manner that could damage, disable, overburden, or impair the
              Service
            </li>
            <li>Collect or store personal data about other users without their consent</li>
            <li>Use the Service to spam, harass, or send unsolicited communications</li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">5. Google API Services</h2>
          <p className="mb-2">
            Our Service uses Google API Services, including Google OAuth for authentication and Google
            Tasks API for task synchronization. By using these features, you also agree to be bound by:
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li>
              <a
                href="https://policies.google.com/privacy"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline"
              >
                Google's Privacy Policy
              </a>
            </li>
            <li>
              <a
                href="https://policies.google.com/terms"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline"
              >
                Google's Terms of Service
              </a>
            </li>
          </ul>
          <p className="mt-2">
            You can revoke the Service's access to your Google account at any time through your Google
            Account settings at{" "}
            <a
              href="https://myaccount.google.com/permissions"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline"
            >
              https://myaccount.google.com/permissions
            </a>
            .
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">6. Intellectual Property Rights</h2>
          
          <h3 className="text-xl font-semibold mb-2 mt-4">6.1 Our Rights</h3>
          <p>
            The Service, including its original content, features, functionality, and all intellectual
            property rights therein, are owned by Homework Scraper, its licensors, or other providers of
            such material and are protected by copyright, trademark, patent, trade secret, and other
            intellectual property or proprietary rights laws.
          </p>

          <h3 className="text-xl font-semibold mb-2 mt-4">6.2 Your Rights</h3>
          <p>
            You retain all rights to any content you provide to the Service, including your homework
            data and educational platform credentials. By using the Service, you grant us a limited,
            non-exclusive, royalty-free license to use, store, and process your content solely for the
            purpose of providing the Service to you.
          </p>

          <h3 className="text-xl font-semibold mb-2 mt-4">6.3 Open Source</h3>
          <p>
            Portions of the Service may be open source software. The applicable open source license
            terms apply to your use of that software.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">7. Service Availability and Modifications</h2>
          
          <h3 className="text-xl font-semibold mb-2 mt-4">7.1 Service Availability</h3>
          <p>
            We strive to provide reliable service, but we do not guarantee that the Service will be
            available at all times or that it will be uninterrupted, secure, or error-free. The Service
            may be subject to limitations, delays, and other problems inherent in the use of the
            internet and electronic communications.
          </p>

          <h3 className="text-xl font-semibold mb-2 mt-4">7.2 Maintenance and Updates</h3>
          <p>
            We may perform scheduled or unscheduled maintenance, updates, or modifications to the
            Service. We will use reasonable efforts to notify you of any scheduled maintenance that may
            significantly impact service availability.
          </p>

          <h3 className="text-xl font-semibold mb-2 mt-4">7.3 Educational Platform Dependencies</h3>
          <p>
            The Service relies on third-party educational platforms (TAMO, eVartai, Mano Dienynas). We
            are not responsible for any changes, disruptions, or limitations to these platforms that may
            affect our ability to scrape homework data. If these platforms change their structure or
            access policies, functionality may be temporarily or permanently affected.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">8. Disclaimers and Limitations of Liability</h2>
          
          <h3 className="text-xl font-semibold mb-2 mt-4">8.1 Warranty Disclaimer</h3>
          <p className="mb-2">
            THE SERVICE IS PROVIDED ON AN "AS IS" AND "AS AVAILABLE" BASIS WITHOUT WARRANTIES OF ANY
            KIND, EITHER EXPRESS OR IMPLIED. TO THE FULLEST EXTENT PERMISSIBLE UNDER APPLICABLE LAW, WE
            DISCLAIM ALL WARRANTIES, INCLUDING BUT NOT LIMITED TO:
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li>Warranties of merchantability, fitness for a particular purpose, and non-infringement</li>
            <li>Warranties regarding the accuracy, reliability, or completeness of the Service</li>
            <li>Warranties that the Service will be uninterrupted, secure, or error-free</li>
            <li>Warranties regarding the results obtained from using the Service</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2 mt-4">8.2 Accuracy of Information</h3>
          <p>
            While we strive to accurately scrape and display homework information, we do not guarantee
            the accuracy, completeness, or timeliness of any homework data displayed in the Service. You
            should always verify important information directly with your educational platform. We are
            not responsible for any consequences resulting from reliance on the homework data provided
            by the Service.
          </p>

          <h3 className="text-xl font-semibold mb-2 mt-4">8.3 Limitation of Liability</h3>
          <p className="mb-2">
            TO THE MAXIMUM EXTENT PERMITTED BY LAW, IN NO EVENT SHALL HOMEWORK SCRAPER, ITS OFFICERS,
            DIRECTORS, EMPLOYEES, OR AGENTS BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL,
            CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING WITHOUT LIMITATION:
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li>Loss of profits, data, use, goodwill, or other intangible losses</li>
            <li>Damages resulting from your use or inability to use the Service</li>
            <li>Unauthorized access to or alteration of your transmissions or data</li>
            <li>Statements or conduct of any third party on the Service</li>
            <li>Any other matter relating to the Service</li>
          </ul>
          <p className="mt-2">
            WHETHER BASED ON WARRANTY, CONTRACT, TORT (INCLUDING NEGLIGENCE), OR ANY OTHER LEGAL THEORY,
            EVEN IF WE HAVE BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
          </p>
          <p className="mt-2">
            IN JURISDICTIONS THAT DO NOT ALLOW THE EXCLUSION OR LIMITATION OF LIABILITY FOR INCIDENTAL
            OR CONSEQUENTIAL DAMAGES, OUR LIABILITY SHALL BE LIMITED TO THE MAXIMUM EXTENT PERMITTED BY
            LAW.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">9. Indemnification</h2>
          <p>
            You agree to defend, indemnify, and hold harmless Homework Scraper and its officers,
            directors, employees, contractors, agents, and affiliates from and against any claims,
            damages, obligations, losses, liabilities, costs, or expenses (including attorneys' fees)
            arising from:
          </p>
          <ul className="list-disc pl-6 space-y-2 mt-2">
            <li>Your use of or access to the Service</li>
            <li>Your violation of these Terms</li>
            <li>Your violation of any third-party rights, including any intellectual property right</li>
            <li>
              Your violation of any applicable laws, rules, or regulations in connection with the
              Service
            </li>
            <li>Any content you submit through the Service</li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">10. Privacy and Data Protection</h2>
          <p>
            Your use of the Service is also governed by our Privacy Policy. Please review our{" "}
            <a
              href="/privacy"
              className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline"
            >
              Privacy Policy
            </a>
            , which explains how we collect, use, and disclose information that pertains to your
            privacy. By using the Service, you consent to our collection and use of personal data as
            outlined in our Privacy Policy.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">11. Termination</h2>
          
          <h3 className="text-xl font-semibold mb-2 mt-4">11.1 Termination by You</h3>
          <p>
            You may terminate your account at any time by accessing your account settings and following
            the account deletion process. Upon termination, your right to use the Service will
            immediately cease.
          </p>

          <h3 className="text-xl font-semibold mb-2 mt-4">11.2 Termination by Us</h3>
          <p className="mb-2">
            We may terminate or suspend your account and access to the Service immediately, without
            prior notice or liability, for any reason, including but not limited to:
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li>Breach of these Terms</li>
            <li>Violation of applicable laws or regulations</li>
            <li>Fraudulent, abusive, or illegal activity</li>
            <li>Extended periods of inactivity</li>
            <li>Technical or security reasons</li>
          </ul>

          <h3 className="text-xl font-semibold mb-2 mt-4">11.3 Effect of Termination</h3>
          <p>
            Upon termination, all rights and licenses granted to you under these Terms will immediately
            cease. We will delete or anonymize your data in accordance with our Privacy Policy.
            Provisions of these Terms that by their nature should survive termination shall survive,
            including but not limited to ownership provisions, warranty disclaimers, indemnity, and
            limitations of liability.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">12. Dispute Resolution</h2>
          
          <h3 className="text-xl font-semibold mb-2 mt-4">12.1 Informal Resolution</h3>
          <p>
            If you have any dispute with us, you agree to first contact us at sadyvod19@gmail.com and
            attempt to resolve the dispute informally. We will work with you in good faith to resolve
            any disputes.
          </p>

          <h3 className="text-xl font-semibold mb-2 mt-4">12.2 Governing Law</h3>
          <p>
            These Terms shall be governed by and construed in accordance with the laws of Lithuania,
            without regard to its conflict of law provisions.
          </p>

          <h3 className="text-xl font-semibold mb-2 mt-4">12.3 Jurisdiction</h3>
          <p>
            Any legal action or proceeding arising under these Terms shall be brought exclusively in the
            courts of Lithuania, and you hereby consent to personal jurisdiction and venue therein.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">13. Changes to Terms</h2>
          <p>
            We reserve the right to modify these Terms at any time. If we make material changes to these
            Terms, we will notify you by:
          </p>
          <ul className="list-disc pl-6 space-y-2 mt-2">
            <li>Posting the updated Terms on this page with a new "Last Updated" date</li>
            <li>Sending an email notification to the address associated with your account</li>
            <li>Displaying a prominent notice within the Service</li>
          </ul>
          <p className="mt-2">
            Your continued use of the Service after any changes to these Terms constitutes your
            acceptance of such changes. If you do not agree to the modified Terms, you must stop using
            the Service and delete your account.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">14. Miscellaneous</h2>
          
          <h3 className="text-xl font-semibold mb-2 mt-4">14.1 Entire Agreement</h3>
          <p>
            These Terms, together with our Privacy Policy, constitute the entire agreement between you
            and Homework Scraper regarding the Service and supersede all prior agreements and
            understandings.
          </p>

          <h3 className="text-xl font-semibold mb-2 mt-4">14.2 Severability</h3>
          <p>
            If any provision of these Terms is held to be invalid or unenforceable, the remaining
            provisions will remain in full force and effect.
          </p>

          <h3 className="text-xl font-semibold mb-2 mt-4">14.3 Waiver</h3>
          <p>
            No waiver of any term of these Terms shall be deemed a further or continuing waiver of such
            term or any other term, and our failure to assert any right or provision under these Terms
            shall not constitute a waiver of such right or provision.
          </p>

          <h3 className="text-xl font-semibold mb-2 mt-4">14.4 Assignment</h3>
          <p>
            You may not assign or transfer these Terms or your rights hereunder, in whole or in part,
            without our prior written consent. We may assign these Terms at any time without notice or
            consent.
          </p>

          <h3 className="text-xl font-semibold mb-2 mt-4">14.5 No Third-Party Beneficiaries</h3>
          <p>
            These Terms do not and are not intended to confer any rights or remedies upon any person
            other than you and us.
          </p>

          <h3 className="text-xl font-semibold mb-2 mt-4">14.6 Force Majeure</h3>
          <p>
            We shall not be liable for any delay or failure to perform resulting from causes outside our
            reasonable control, including but not limited to acts of God, war, terrorism, riots,
            embargoes, acts of civil or military authorities, fire, floods, accidents, strikes, or
            shortages of transportation facilities, fuel, energy, labor, or materials.
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">15. Educational Purpose Disclaimer</h2>
          <p>
            This Service is designed to help students manage their homework assignments more effectively.
            However:
          </p>
          <ul className="list-disc pl-6 space-y-2 mt-2">
            <li>
              You are solely responsible for completing your homework and meeting academic requirements
            </li>
            <li>The Service is a tool to assist organization, not a substitute for diligent study</li>
            <li>
              You must comply with your school's academic integrity policies and honor code
            </li>
            <li>
              We are not affiliated with any educational institution or educational platform provider
            </li>
          </ul>
        </section>

        <section>
          <h2 className="text-2xl font-bold mb-3">16. Contact Information</h2>
          <p className="mb-2">
            If you have any questions about these Terms, please contact us at:
          </p>
          <div className="pl-6">
            <p>
              <strong>Email:</strong> sadyvod19@gmail.com
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

        <section className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <p className="text-sm">
            <strong>By using Homework Scraper, you acknowledge that you have read, understood, and agree
            to be bound by these Terms of Service.</strong>
          </p>
        </section>
      </div>
    </div>
  );
}
