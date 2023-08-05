/*
Copyright 2010-2012 SourceGear, LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

******************************************************************************
This file has been modified to create a more generic default configuration.
******************************************************************************
*/

function printUsageError()
{
    print("Usage: init_builds.js REPO_NAME");
}

function init_builds(repo)
{
    var manualSeriesRecId;
    var manualStatusRecId;
    var zrec;

    var zdb = new zingdb(repo, sg.dagnum.BUILDS);
    var ztx = zdb.begin_tx();



    // Environments

    zrec = ztx.new_record("environment");
    zrec.name = "Windows ";
    zrec.nickname = "W";

    zrec = ztx.new_record("environment");
    zrec.name = "Mac";
    zrec.nickname = "M";

    zrec = ztx.new_record("environment");
    zrec.name = "Linux";
    zrec.nickname = "L";



    // Series

    zrec = ztx.new_record("series");
    manualSeriesRecId = zrec.recid;
    zrec.name = "Manual";
    zrec.nickname = "M";

    zrec = ztx.new_record("series");
    zrec.name = "Nightly";
    zrec.nickname = "N";

    zrec = ztx.new_record("series");
    zrec.name = "Continuous";
    zrec.nickname = "C";



    // Status (Q)

    zrec = ztx.new_record("status");
    manualStatusRecId = zrec.recid;
    zrec.name = "Queued";
    zrec.nickname = "Q";
    zrec.color = "white";
    zrec.temporary = true;
    zrec.successful = false;
    zrec.use_for_eta = false;
    zrec.show_in_activity = true;
    zrec.icon = "queued";

    // Status (U)

    zrec = ztx.new_record("status");
    zrec.name = "Updating";
    zrec.nickname = "U";
    zrec.color = "gray";
    zrec.temporary = true;
    zrec.successful = false;
    zrec.use_for_eta = true;
    zrec.show_in_activity = false;
    zrec.icon = "skip";

    zrec = ztx.new_record("status");
    zrec.name = "Update Failed";
    zrec.nickname = "UF";
    zrec.color = "red";
    zrec.temporary = false;
    zrec.successful = false;
    zrec.use_for_eta = false;
    zrec.show_in_activity = true;
    zrec.icon = "buildfailed";

    // Status (B)

    zrec = ztx.new_record("status");
    zrec.name = "Building";
    zrec.nickname = "B";
    zrec.color = "yellow";
    zrec.temporary = true;
    zrec.successful = false;
    zrec.use_for_eta = true;
    zrec.show_in_activity = false;
    zrec.icon = "build";

    zrec = ztx.new_record("status");
    zrec.name = "Build Failed";
    zrec.nickname = "BF";
    zrec.color = "red";
    zrec.temporary = false;
    zrec.successful = false;
    zrec.use_for_eta = false;
    zrec.show_in_activity = true;
    zrec.icon = "buildfailed";

    // Status (T)

    zrec = ztx.new_record("status");
    zrec.name = "Testing";
    zrec.nickname = "T";
    zrec.color = "yellow";
    zrec.temporary = true;
    zrec.successful = false;
    zrec.use_for_eta = true;
    zrec.show_in_activity = false;
    zrec.icon = "testing";

    zrec = ztx.new_record("status");
    zrec.name = "Test Failed";
    zrec.nickname = "TF";
    zrec.color = "red";
    zrec.temporary = false;
    zrec.successful = false;
    zrec.use_for_eta = false;
    zrec.show_in_activity = true;
    zrec.icon = "testfailed";

    // Status (C)

    zrec = ztx.new_record("status");
    zrec.name = "Checking";
    zrec.nickname = "C";
    zrec.color = "yellow";
    zrec.temporary = true;
    zrec.successful = false;
    zrec.use_for_eta = true;
    zrec.show_in_activity = false;
    zrec.icon = "coverage";

    zrec = ztx.new_record("status");
    zrec.name = "Check Failed";
    zrec.nickname = "CF";
    zrec.color = "red";
    zrec.temporary = false;
    zrec.successful = false;
    zrec.use_for_eta = false;
    zrec.show_in_activity = true;
    zrec.icon = "testfailed";

    // Status (D)

    zrec = ztx.new_record("status");
    zrec.name = "Done";
    zrec.nickname = "D";
    zrec.color = "green";
    zrec.temporary = false;
    zrec.successful = true;
    zrec.use_for_eta = false;
    zrec.show_in_activity = true;
    zrec.icon = "success";



    var recs = zdb.query("config", ["recid"]);
    if (recs == null || recs.length == 0)
    {
        zrec = ztx.new_record("config");
        zrec.manual_build_series = manualSeriesRecId;
        zrec.manual_build_status = manualStatusRecId;
    }

    var r = ztx.commit();
    if (r.errors != null)
    {
        ztx.abort();
        print(sg.to_json__pretty_print(r));
    }
    else
    {
        print("Builds initialized.");
    }
}

/******************************************************************
 * MAIN
 ******************************************************************/
var repo;
if (arguments.length == 1)
{
    repo = sg.open_repo(arguments[0]);
    try
    {
        init_builds(repo);
    }
    finally
    {
        repo.close();
    }

}
else
{
    printUsageError();
}
