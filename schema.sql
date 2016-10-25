drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  model text not null,
  sn text not null,
  status text not null,
  user text not null    
);
