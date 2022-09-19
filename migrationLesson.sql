use base_test_sacado;

drop table lesson_connexioneleve;
drop table lesson_event;

--
-- Create model ConnexionEleve
--
CREATE TABLE `lesson_connexioneleve` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `urlJoinEleve` varchar(250) NULL);
--
-- Create model Event
--
CREATE TABLE `lesson_event` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `title` varchar(100) NOT NULL, `start` datetime(6) NOT NULL, `end` datetime(6) NOT NULL, `notification` bool NOT NULL, `comment` longtext NULL, `display` bool NOT NULL, `color` varchar(50) NOT NULL, `urlCreate` varchar(1000) NULL, `urlJoinProf` varchar(250) NULL, `urlJoinEleve` varchar(250) NULL, `urlIsMeetingRunning` varchar(250) NULL, `user_id` integer NULL);
--
-- Add field event to connexioneleve
--
ALTER TABLE `lesson_connexioneleve` ADD COLUMN `event_id` integer NOT NULL , ADD CONSTRAINT `lesson_connexioneleve_event_id_b68b8296_fk_lesson_event_id` FOREIGN KEY (`event_id`) REFERENCES `lesson_event`(`id`);
--
-- Add field user to connexioneleve
--
ALTER TABLE `lesson_connexioneleve` ADD COLUMN `user_id` integer NOT NULL , ADD CONSTRAINT `lesson_connexioneleve_user_id_cfc182ed_fk_account_user_id` FOREIGN KEY (`user_id`) REFERENCES `account_user`(`id`);
ALTER TABLE `lesson_event` ADD CONSTRAINT `lesson_event_user_id_6a86e450_fk_account_user_id` FOREIGN KEY (`user_id`) REFERENCES `account_user` (`id`);
