-- SQLite
BEGIN TRANSACTION;
CREATE TEMPORARY TABLE postsbackup(id,class,username,title,body,time,date);
INSERT INTO postsbackup SELECT id,class,username,title,body,time,date FROM posts;
DROP TABLE posts;
CREATE TABLE posts(id,class,username,title,body,time TIME,date DATE);
INSERT INTO posts SELECT id,class,username,title,body,time,date FROM postsbackup;
DROP TABLE postsbackup;
ALTER TABLE posts
ADD year YEAR;
COMMIT;