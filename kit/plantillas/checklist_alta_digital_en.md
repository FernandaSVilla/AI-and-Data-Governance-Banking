# Checklist: an onboarding process that recognises every entry profile

*For product, compliance and customer-experience teams. Each "No" is a point where onboarding may leave out people entitled to an account before any model exists. It should be documented in the DPIA (GDPR Art. 35) or the FRIA (AI Act Art. 27).*

## A. Recognition of each entry profile
| Profile | Check |
|---|---|
| International protection document | [ ] The document selector in digital onboarding includes it and automatic reading has been tested with it. |
| Pending residence number or official receipt | [ ] The process accepts provisional documents and defines which additional verification applies. |
| Non-EU passport without a chip | [ ] If NFC reading fails, an alternative verification exists (optical reading, video call, branch). |
| No fixed address or no proof of address | [ ] Alternatives to proof of address are accepted (self-declaration, certificate from a social service or shelter). |
| Phone or connection not good enough for verification | [ ] If the selfie, NFC, video or SMS step fails, another route is offered (video call, code by other means, branch appointment), not a generic error. |
| Needs help to complete the digital process | [ ] Human help is available (phone, chat or branch) and the form uses plain language. |
| Needs an accessibility adjustment | [ ] The channel works with a screen reader and does not rely only on visual or audio instructions; the adjustment required and whether it was available are logged, never a diagnosis (Directive (EU) 2019/882). |
| No credit history | [ ] The entity knows how many account holders never become scorable and assesses the use of lawful alternative data. |

- [ ] The list of accepted documents is published and consistent across web, app and branch.
- [ ] When the digital channel cannot verify a valid credential, the screen explains why and offers a concrete alternative route.

## B. Recording non-entry
- [ ] Every interrupted onboarding attempt generates a record with its entry profile and one of the nine standardised causes (`registro_no_acceso` schema).
- [ ] A basic payment account application form is available online and in branches, with a reference number and a copy for the applicant.
- [ ] Refusals are communicated in writing with a specific reason (Spain: RDL 19/2017, Art. 5; EU: Directive 2014/92/EU, Art. 16(7)) and the share that complies is measured.

## C. Proportionality before refusal
- [ ] Before refusing on money-laundering risk grounds, an alternative is assessed and recorded (transaction limits, additional verification, enhanced monitoring) (EBA/GL/2023/04).
- [ ] The alternative does not replace the right to a basic payment account when its requirements are met.

## D. Human review and reversal
- [ ] Automatic onboarding refusals can be escalated to a person with decision-making authority.
- [ ] The reversal rate after review is measured by entry profile; a high rate signals false negatives in the process.

## E. Link to AI governance
- [ ] The evaluability report (`python -m evaluabilidad` or the web version) is run at least every six months.
- [ ] Its results are annexed to the FRIA of creditworthiness systems and to post-market monitoring (AI Act Arts. 27 and 72).
- [ ] Profiles with a "Clear signal" trigger a documented review of the onboarding step where they are lost.
