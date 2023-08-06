# !/usr/bin/env python
#
# Author: Paul D. Eden <paul@benchline.org>
# Created: 2014-03-26
"""
Script to automatically create and maintain a sqlite database of project line counts
over time.  It allows multiple projects and is designed to be run unattended from cron
and needs no setup besides for installing sqlite3 and cloc.
"""
import os
import csv
import datetime
import subprocess

import peewee

import benchline.args
import benchline.command


default_db_file = os.path.join(os.path.expanduser("~"), "metrics/line_counts.db")
exclude_list_file = "exclude-list"

db = peewee.SqliteDatabase(default_db_file)


class LineCounts(peewee.Model):
    date_time_stamp = peewee.DateTimeField()
    project = peewee.CharField()
    language = peewee.CharField()
    file = peewee.CharField()
    num_blank = peewee.IntegerField()
    num_comment = peewee.IntegerField()
    num_code = peewee.IntegerField()

    class Meta:
        database = db


# TODO: use db_file_name instead of the default_db_file
# It's hard due to peewee requiring the database object to be ready at
# script compilation time instead of runtime.
def setup_database(db_file_name):
    LineCounts.create_table()


def validate_args(parser, options, args):
    if len(args) < 1 and not options.project_dir:
        parser.error("If not using --project-dir then the first positional argument must be the project name.")
    if options.project_dir:
        if not os.path.exists(options.project_dir):
            parser.error("--project-dir doesn't exist.")
        if not os.path.isdir(options.project_dir):
            parser.error("--project-dir is not a directory.")


def save_row_to_db(row):
    line_counts = LineCounts()
    line_counts.date_time_stamp = datetime.datetime.now()
    line_counts.project = row[5]
    line_counts.language = row[0]
    line_counts.file = row[1]
    line_counts.num_blank = row[2]
    line_counts.num_comment = row[3]
    line_counts.num_code = row[4]
    line_counts.save()


def maven_project():
    return os.path.exists("pom.xml")


def git_project():
    return os.path.exists(".git") and os.path.isdir(".git")


def update_git_project():
    benchline.command.run("git pull")


def update_svn_project():
    benchline.command.run("svn update")


def svn_project():
    return os.path.exists(".svn") and os.path.isdir(".svn")


def clean_maven_project():
    benchline.command.run("mvn clean")
    try:
        benchline.command.run("mvn release:clean")
    except subprocess.CalledProcessError:
        pass


def write_exclude_list():
    with open(exclude_list_file, "w") as f:
        f.write("atlassian-ide-plugin.xml\n")


def delete_exclude_list():
    os.remove(exclude_list_file)


def gather_line_counts(project_name):
    write_exclude_list()
    output_lines = benchline.command.output("cloc --exclude-list-file=exclude-list "
                                            "--exclude-dir=.idea --csv --by-file .").split(os.linesep)
    delete_exclude_list()
    return filter(lambda x: x != [project_name], [row + [project_name] for row in csv.reader(output_lines[5:])])


def count_maven_project(project_name):
    clean_maven_project()
    return gather_line_counts(project_name)


def count_generic_project(project_name):
    return gather_line_counts(project_name)


def database_is_setup(db_file_str):
    return os.path.exists(db_file_str)


def update_project():
    if git_project():
        update_git_project()
    elif svn_project():
        update_svn_project()


def cd_then_count_projects(project_dir, project_name, database_file):
    os.chdir(os.path.join(project_dir, project_name))
    count_lines_for_project(project_name, database_file)


def count_lines_for_project(project_name, database_file):
    update_project()
    if maven_project():
        rows = count_maven_project(project_name)
    else:
        rows = count_generic_project(project_name)
    if not database_is_setup(database_file):
        setup_database(database_file)
    map(save_row_to_db, rows)


def count_lines_for_projects_in_project_dir(project_dir, database_file):
    map(lambda x: cd_then_count_projects(project_dir, x, database_file), os.listdir(project_dir))


def main():
    parser = benchline.args.make_parser(usage="usage: %%prog [options] [project_name]\n%s" % __doc__)
    parser.add_option("--db-file", action="store_true", default=default_db_file,
                      help="sqlite database file to save to.  default=%s" % default_db_file)
    parser.add_option("-d", "--project-dir",
                      help="Count the lines in all the projects in this directory.  It goes one level deep only.")
    options, args = benchline.args.triage(parser, validate_args=validate_args)

    if options.project_dir:
        project_dir = options.project_dir
        if "~" in options.project_dir:
            project_dir = os.path.join(os.path.expanduser("~"), options.project_dir.replace("~", ""))
        count_lines_for_projects_in_project_dir(project_dir, options.db_file)
    else:
        count_lines_for_project(args[0], options.db_file)


if __name__ == "__main__":
    main()
