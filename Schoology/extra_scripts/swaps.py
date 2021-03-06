import AR.AR as AR
import AR.schoology as schoology
import asyncio
import csv
import sys

clashing_ids = ['91932', '88150', '91579', '85460', '86829', '91137', '91365',
                '87331', '92063', '86157', '91847', '91501', '88710', '89008', '92279',
                '91832', '86341', '91097', '88334', '91017', '92196', '86951', '88605',
                '88990', '90071', '88314', '88330', '92679', '84026', '92075', '87937',
                '86787', '92122', '87699', '85620', '90079', '87992', '91009', '91424',
                '91150', '87818', '92109', '86727', '90636', '88848', '87867', '87648',
                '81417', '91240', '90223', '91064', '87349', '85412', '92230', '90102',
                '92622', '90982', '90431', '85329', '91697', '82809', '91890', '85565',
                '86895', '82819', '90599', '91799', '91219', '89031', '87972', '88324',
                '88673', '89559', '87569', '90226', '94260', '92240', '87139', '88275',
                '86973', '92492', '87964', '93223', '83886', '83249', '83697', '91840',
                '91082', '92340', '92229', '92950', '88993', '86371', '94256', '88840',
                '94030', '91841', '85714', '89520', '90673', '86722', '86139', '89663',
                '87546', '88997', '82962', '87256', '89053', '93633', '83592', '92645',
                '83747', '90113', '90967', '85996', '92195', '91460', '88454', '91861',
                '85617', '87634', '83296', '90485', '91652', '88290', '89804', '89532',
                '91784', '88704', '87308', '93266', '89170', '89263', '93497', '87076',
                '92749', '90320', '93201', '92621', '93259', '90883', '85564', '90354',
                '93239', '83856', '87233', '92625', '88818', '86342', '93100', '83289',
                '91027', '86276', '89685', '88575', '87603', '90863', '83828', '92111',
                '90685', '83038', '86431', '91568', '90984', '90157', '89971', '87577',
                '90086', '93095', '91430', '85208', '88816', '81090', '90829', '90980',
                '91877', '92665', '90675', '86884', '92800', '94141', '86309', '87325',
                '89035', '85484', '88304', '85390', '93096', '90873', '88697', '88322',
                '85258', '94255', '93278', '88014', '90061', '88359', '92193', '90927',
                '86955', '88821', '88685', '90770', '93405', '89178', '89128', '86219',
                '90139', '92353', '89451', '86607', '87590', '86731', '87199', '87305',
                '89884', '88455', '87744', '88021', '87999', '86261', '92104', '91113',
                '89205', '91402', '87553', '91864', '92091', '92692', '89002', '90384',
                '93478', '87028', '89092', '91971', '89733', '92828', '91090', '82944',
                '89749', '87019', '84039', '86312', '92043', '92198', '92992', '87102',
                '89595', '86258', '89407', '88490', '89271', '91401', '90201', '85176',
                '86852', '88246', '93083', '93339', '91947', '86926', '92213', '90106',
                '90160', '88136', '90390', '83992', '89853', '88099', '91215', '89666',
                '82966', '92000', '91128', '92866', '92696', '87547', '90162', '91712',
                '87576', '92318', '88743', '89009', '92381', '90583', '92572', '83620',
                '86010', '87460', '91300', '93829', '87986', '86225', '88125', '89251',
                '88408', '88688', '87326', '89023', '91949', '91846', '87581', '82872',
                '86877', '91023', '88695', '88438', '83953', '89926', '81396', '89489',
                '90219', '90826', '92087', '90901', '88481', '86190', '86189', '89306',
                '85989', '92056', '91986', '93197', '93018', '93516', '90962', '91196',
                '90045', '87743', '87639', '88658', '87858', '91056', '89503', '89423',
                '85217', '90446', '91992', '85994', '85541', '83436', '85085', '91126',
                '93903', '90985', '85416', '87244', '92917', '88892', '93426', '91786',
                '85365', '92865', '91383', '86109', '92057', '89678', '89519', '92702',
                '89429', '82964', '86969', '87316', '86861', '83947', '89592', '86933',
                '86897', '85531', '87453', '91960', '87582', '87520', '83845', '88407',
                '91468', '93374', '89812', '92691', '82871', '88870', '88574', '90783',
                '90804', '91723', '86231', '91309', '93191', '87524', '90238', '87963',
                '93025', '88329', '86864', '86046', '86155', '92162', '87544', '92392',
                '83751', '90854', '87070', '91304', '91812', '83756', '86802', '88918',
                '87170', '90658', '88459', '92317', '91357', '90252', '90310', '92106',
                '90672', '88716', '89847', '92328', '89591', '92619', '91130', '90087',
                '92929', '90966', '93868', '93089', '90432', '86838', '87654', '88349',
                '88247', '91012', '88260', '93367', '93992', '92237', '87088', '89623',
                '92246', '88678', '87514', '86205', '93008', '90153', '88319', '88416',
                '85468', '91048', '88588', '91651', '89197', '94204', '90405', '91865',
                '91220', '91473', '85624', '89585', '92144', '87879', '90612', '91718',
                '85354', '85432', '86881', '83883', '85393', '90839', '88400', '87048',
                '92693', '88253', '88456', '86747', '84164', '88114', '89662', '85627',
                '90393', '91095', '94049', '89214', '91950', '87516', '88488', '90511',
                '90333', '88826', '91257', '88507', '91595', '82943', '90180', '88472',
                '85567', '87311', '90540', '89410', '89110', '90084', '86734', '90794',
                '89113', '90832', '82284', '92640', '85701', '91567', '90375', '94257',
                '89427', '83667', '91851', '91982', '89805', '87989', '89211', '87762',
                '94196', '84256', '89231', '90598', '90721', '90414', '83624', '91918',
                '94254', '91845', '88709', '92143', '93184', '91981', '82905', '93366',
                '91028', '88616', '87467', '82864', '91860', '87666', '93804', '87432',
                '89799', '91970', '90828', '94259', '93272', '89861', '91361', '89558',
                '92684', '90050', '90903', '89292', '91429', '86737', '92658', '91759',
                '93532', '82907', '90204', '82316', '91707', '92294', '88731', '86119',
                '83984', '91420', '83963', '87754', '91198', '83765', '88861', '86847',
                '85187', '86985', '83837', '91472', '86221', '87649', '90571', '90430',
                '87583', '88677', '90400', '83734', '89449', '84078', '93093', '85410',
                '94223', '90296', '92272', '88650', '92205', '83805', '91092', '90085',
                '88148', '90199', '92709', '85063', '86166', '88420', '83831', '91978',
                '86045', '89668', '93375', '85555', '89571', '90365', '88615', '87265',
                '87534', '93964', '87580', '94252', '89233', '86016', '89943', '92953',
                '87051', '91867', '88866', '92670', '89651', '86896', '83836', '91026',
                '91868', '86851', '86800', '92642', '92632', '89747', '88525', '93124',
                '92217', '82780', '89247', '92034', '87077', '93279', '90547', '86066',
                '89032', '90125', '91908', '89317', '87739', '92859', '87619', '93211',
                '89224', '93826', '92960', '92352', '90120', '88846', '89107', '89510',
                '89479', '92053', '89594', '93185', '92982', '92520', '92543', '90674',
                '83310', '92759', '87974', '90784', '90473', '89657', '91635', '88152',
                '90266', '88925', '88780', '89779', '87480', '90671', '85893', '83051',
                '87027', '92228', '88890', '92853', '93090', '90851', '89934', '91305',
                '87136', '89059', '89198', '90416', '88847', '86718', '91578', '89212',
                '86941', '90246', '90654', '83077', '88932', '89177', '87452', '89142',
                '92981', '87239', '85348', '84196', '91406', '90423', '91436', '87535',
                '90513', '86169', '86479', '92535', '85251', '92095', '93520', '89208',
                '85347', '90156', '85520', '93875', '87519', '90094', '82865', '92525',
                '90362', '91006', '86003', '90119', '93068', '82895', '87913', '90415',
                '91564', '87890', '87527', '88817', '83750', '90679', '88442', '92615',
                '89536', '91829', '88120', '91863', '91186', '85415', '87918', '87113',
                '87541', '89633', '90796', '92706', '92675', '92825', '83013', '85243',
                '92869', '88271', '82947', '85589', '90653', '91148', '87185', '91193',
                '83798', '88729', '89191', '91577', '94070', '87921', '90680', '83672',
                '89097', '91187', '88620', '81411', '88326', '87587', '86719', '89765',
                '87785', '90969', '86999', '91173', '89965', '88119', '86935', '87110',
                '86543', '91500', '90351', '90694', '89350', '91681', '92802', '87825',
                '90613', '89684', '90878', '91461', '89776', '87426', '84048', '93800',
                '86181', '88623', '87936', '85307', '93353', '87636', '92635', '90602',
                '90647', '83193', '92956', '82836', '89115', '90779', '92187', '93145',
                '88419', '92233', '87660', '93973', '83715', '90505', '93265', '83783',
                '91936', '91844', '82983', '90970', '91502', '87089', '91803', '89054',
                '92032', '85168', '90099', '83948', '84249', '90261', '90370', '85020',
                '87667', '87489', '85871', '91492', '91203', '89586', '83858', '89580',
                '93987', '90213', '82923', '86218', '94203', '88368', '90536', '87604',
                '90253', '90848', '87692', '90592', '89020', '90688', '92660', '83606',
                '91421', '90046', '86356', '91859', '92710', '90594', '90965', '90563',
                '89033', '89648', '89331', '92650', '83821', '85192', '88657', '87226',
                '88467', '85384', '91491', '92999', '92170', '90130', '91049', '90693',
                '90871', '83717', '91828', '86322', '92197', '87966', '90827', '85358',
                '94253', '90483', '93883', '86902', '86469', '87481', '89169', '88124',
                '91287', '90321', '89611', '89878', '86421', '87955', '90123', '90194',
                '91076', '90586', '89462', '93735', '89252', '90922', '89883', '92014',
                '82875', '92624', '87912', '88891', '84058', '89906', '89095', '90621',
                '90361', '91634', '91624', '91559', '92232', '92384', '93939', '88556',
                '85366', '89924', '85291', '86120', '91763', '89658', '85233', '86511',
                '89723', '90158', '85206', '89910', '87725', '91899', '88372', '90164',
                '90134', '89168', '83801', '83727', '89336', '85539', '90537', '90745',
                '86798', '89326', '87350', '91392', '86775', '90371', '92171', '88258',
                '91825', '91843', '93519', '90111', '92241' ]

async def delete_clashing_emails(environment, genesis_ids):
      """
      Looks up who has a clashing email, changes it to a unique, dummy email
      """
      async with schoology.Session(environment) as Schoology:
            async with Schoology.Users as Users:
                  results = await Users.csvexport(['mail', 'school_uid'])
                  schoology_emails = {}
                  for row in csv.reader(results.splitlines()[1:]):
                        schoology_emails[str(row[0]).upper()] = str(row[1])
                  for genesis_id in genesis_ids:
                        student = AR.student_by_id(genesis_id)
                        email = student.email
                        if email == None or email.upper() not in schoology_emails:
                              print(email)
                              print(f"Unable to determine email for {student}")
                              continue
                        clashing_student = AR.student_by_id(schoology_emails[student.email.upper()])
                        print(f"{genesis_id} needs the email address {student.email} but "
                              f"{clashing_student.student_id} currently has it.")
                        await Users.add_update(
                              school_uid=clashing_student.student_id,
                              name_first=clashing_student.first_name,
                              name_last=clashing_student.last_name,
                              email=clashing_student.student_id + "@monroe.k12.nj.us",
                              role='Student',
                        )

loop = asyncio.get_event_loop()
AR.init('../databases/2019-09-16-genesis.db')
loop.run_until_complete(delete_clashing_emails('production', clashing_ids))
loop.close()
