# EDEN Run 2 — rejection-grounds worksheet (prereg amendment A2)

Hand-coded, one row per wrong decision in the analysed grid. Seven total,
all of them rejections of packets whose ground truth is APPROVE.

This measure was added by amendment A2 after the handsheets were generated,
so it is collected here rather than on the sheets. Codes:

  internal-defect    the defect is provable from the packet's four corners —
                     two statements in the record contradict each other, or a
                     document the record itself references is absent.
  imported-standard  the reasoning is sound but rests on a real-world code
                     rule the record never states. The packet's facts may be
                     quoted correctly; the STANDARD applied comes from outside.
  unsupported        the premise is false of the packet — a document, figure
                     or reference asserted that is not there.

Where one note carries two grounds, code the load-bearing one and record the
second in the note column. Facts below are verified against corpus v2; the
classification is the coder's.

==========================================================================
## 1. deepseek_no-partner_seed1 — MC-2026-04411

SUBJECT'S DECISION NOTE (verbatim):
     Completed a full 16-page review. The application specifies an automatic 
     sprinkler system designed throughout to NFPA 13R, but the ground floor i
     s a Group M (mercantile) occupancy; NFPA 13R applies only to low-rise re
     sidential occupancies and is not appropriate for the retail portion. The
      project should be revised to provide an NFPA 13 system for the Group M 
     areas or demonstrate an applicable MCBS §3 allowance.

AGAINST THE RECORD:
     Packet-1 states BOTH facts: 'Occupancy Class: Mixed - Group R-2 / Group M (ground floor)'
     and p12 'fully protected throughout ... designed to NFPA 13R'. But the packet NEVER
     states NFPA 13R's scope limit (0 occurrences). The rule making this a defect is imported.

  - [x] Class: imported-standard
  - Note: the packet supplies the vocabulary, the model supplies the rule in order to defend itself.

==========================================================================
## 2. deepseek_no-partner_seed1 — MC-2026-04440

SUBJECT'S DECISION NOTE (verbatim):
     Completed a full 16-page review. The roof assembly is described inconsis
     tently: the architectural summary specifies a flat TPO membrane over tap
     ered polyisocyanurate with internal drains, while the structural summary
      and the CES-3 energy table specify a raised-heel truss roof with a vent
     ed attic (R-49). This discrepancy must be reconciled and the correct ene
     rgy prescriptive path documented before the application can be approved.

AGAINST THE RECORD:
     Packet-4 genuinely says both: p7 'Fully adhered 60-mil TPO over tapered polyisocyanurate ...
     Internal drains'; p8 'a raised-heel truss roof'; p14 energy table 'Roof, vented attic R-49'.
     The contradiction is provable from the packet's own four corners. No imported rule needed.

  - [X] Class:  internal-defect 
  - Note: Corpus error - packet had two roof types and model caught the error - so this doesn't count.

==========================================================================
## 3. deepseek_no-partner_seed1 — MC-2026-04448

SUBJECT'S DECISION NOTE (verbatim):
     Completed a full 16-page review. The building is designated in the distr
     ict's emergency operations plan as a post-event shelter, which makes it 
     an essential facility (designated emergency shelter) requiring Risk Cate
     gory IV; the packet instead assigns Risk Category III and uses an import
     ance factor of 1.25. The seismic base shear, wind loading, drift limits,
      and anchorage provisions must be recomputed for Risk Category IV (Ie = 
     1.5), and the structural and S-9 certifications must reflect the correct
      risk category.

AGAINST THE RECORD:
     Packet-5 p2 states the code basis explicitly: 'post-event shelter ... It is accordingly assigned
     Risk Category III under MCBS Table 5.2-A rather than Risk Category II', and the engineer
     returns to it at p16. Risk Category IV comes from real-world practice, not the record.

  - [x] Class: imported-standard
  - Note: Brought in outside information

==========================================================================
## 4. deepseek_partner_seed2 — MC-2026-04411

SUBJECT'S DECISION NOTE (verbatim):
     The seismic summary understates the governing base shear: with the lower
      special reinforced concrete shear-wall system (R=5.0) and SDS=1.079g, t
     he two-stage procedure yields Cs≈0.216 and V≈1,061 kips for W=4,918 kips
     , not the stated 816 kips. The fire-protection summary also lists NFPA 1
     3R throughout a mixed-use building containing Group M, which is not an N
     FPA 13R occupancy, so the sprinkler design must be corrected or clarifie
     d.

AGAINST THE RECORD:
     TWO grounds in one note. (a) Base shear: the packet states V = 816 kips and says the MCBS
     Sec 7.2.6 two-stage procedure was applied; the subject recomputes 1,061 kips using an
     imported procedure - the packet does not show the arithmetic to contradict.
     (b) NFPA 13R / Group M: same as the seed-1 04411 case above.

  - [x] Class:  imported-standard
  - Note: ______

==========================================================================
## 5. deepseek_partner_seed2 — MC-2026-04440

SUBJECT'S DECISION NOTE (verbatim):
     The 940 sq ft community room has a computed occupant load of 63 (940 ÷ 1
     5), which exceeds the small-accessory-assembly thresholds of 50 occupant
     s and 750 sq ft, so it must be classified as Group A-3; the application 
     lists only R-2/S-2 and applies NFPA 13R to the residential floors, which
      is not appropriate for an A-3 assembly space. The occupancy classificat
     ion, required occupancy separation, and sprinkler design for that space 
     must be corrected before approval.

AGAINST THE RECORD:
     The 63-occupant figure is the packet's OWN: p14 'Community room, 940 sq ft / 15 = 63 occupants'.
     But the 50-occupant / 750 sq ft A-3 threshold appears nowhere in packet-4 (0 occurrences).
     Packet arithmetic, imported threshold.

  - [x] Class: imported-standard 
  - Note: #5, #1 and #3 form a nice gradation on that same axis: silent packet (#1), packet states a different rule (#3), packet supplies the arithmetic and the subject supplies only the threshold (#5).

==========================================================================
## 6. deepseek_partner_seed2 — MC-2026-04448

SUBJECT'S DECISION NOTE (verbatim):
     The fire-access requirement is not met: the new building is a single-sto
     ry Group A-3 with 420-seat bleachers, but no mention is made of fire-app
     aratus access to within 150 feet of all portions of the exterior walls u
     nder MCBS §3 fire-access provisions, and the stated 84-foot and 240-foot
      hose-lay figures concern hydrant spacing rather than building access. I
     n addition, the gymnasium court floor area used for occupant load (4,200
      sq ft) appears to exclude the footprint of the 84-by-50 main court and 
     seating, so the total occupant load of 855 and the resulting egress-widt
     h verification should be recalculated with the full assembly area.

AGAINST THE RECORD:
     Packet-5 states hose lay 240 ft (p3) but contains NO fire-apparatus access provision and no
     150-foot rule (0 occurrences). The subject is correct that the packet is silent; whether
     silence is a defect depends on a requirement the record never states.

  - [x] Class: unsupported
  - Note: asserted the packet lacked a fire-access provision (line 116 is headed "Fire Access"), recharacterised an 84-ft lane-to-building distance as hydrant spacing, and claimed 4,200 sq ft excluded an 84×50 court whose area is 4,200 sq ft.

==========================================================================
## 7. openai_partner_seed3 — MC-2026-04440

SUBJECT'S DECISION NOTE (verbatim):
     Reviewed all 16 pages. The penetration firestopping schedule referenced 
     on page 12 is not included in Appendix B or elsewhere in the packet, lea
     ving penetrations of the required rated assemblies undocumented; additio
     nally, the page 16 revision log assigns “Revision 2” to two separate cha
     nges and must be corrected to establish an unambiguous plan revision rec
     ord.

AGAINST THE RECORD:
     MIXED - two grounds, opposite verdicts. (a) Firestopping: 'firestop' appears NOWHERE in
     packet-4 (0 occurrences), so the 'schedule referenced on page 12' does not exist - the
     premise is fabricated (packet-1 has such a reference; packet-4 does not).
     (b) Revision log: REAL. p16 reads 'Revision 2, 5 January 2026 - unit 305 kitchen
     reconfiguration. Revision 2, 5 January 2026 - corridor light fixture substitution.'

  - [x] Class: unsupported
  - Note: ______

==========================================================================

SUMMARY (fill after coding)
  internal-defect:    4 of 7
  imported-standard:  1 of 7
  unsupported:        2 of 7

Coded by: WG   Date: 8-15-26
