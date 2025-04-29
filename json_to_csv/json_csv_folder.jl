using JSON, CSV, DataFrames, Dates

folder_name = "test"

fdf = DataFrame(participation_code = String[], level_id = String[], 
    start_treasury = Int64[], no_rounds = Int64[], user_id = String[], timestamp = Int64[], readable_timestamp = DateTime[], start_approval = Int64[],
    country = String[], round_number = Int64[], action_number = Int64[], population = Int64[], round_start_treasury = Int64[], current_treasury = Int64[], action = String[],
    cost = Int64[], x_loc = Int64[], y_loc = Int64[])
files = readdir(pwd() * "\\" * folder_name)

for file in files 
    level = JSON.parsefile(folder_name * "/" * file)
    df = DataFrame(level)
    participation_code = df[!,:meta][1]["participation_code"]
    level_id = df[!,:meta][1]["level_id"]
    start_treasury = parse(Int,df[!,:meta][1]["startTreasury"])
    no_rounds = parse(Int,df[!,:meta][1]["noOfRounds"])
    user_id = df[!,:meta][1]["user_id"]
    timestamp = df[!,:meta][1]["timestamp"]
    readable_timestamp = unix2datetime(timestamp)
    start_approval = parse(Int,df[!,:meta][1]["startApproval"])
    country = df[!,:meta][1]["country"]
    cround = df[!,:round]
    for i in eachindex(cround)
        round_number = cround[i]["roundNumber"]
        population = cround[i]["population"]
        treasury = cround[i]["treasury"]
        current_treasury = cround[i]["treasury"]
        turn = cround[i]["turn"]
        if isempty(turn)
            push!(fdf, [participation_code level_id start_treasury no_rounds user_id timestamp readable_timestamp start_approval country round_number 0 population treasury treasury "PASS" 0 -1 -1])
        else
            for j in eachindex(turn)
                cost = parse(Int,turn[j]["cost"])
                if turn[j]["action"] == "CHOP"
                    cost = -1 * cost
                end
                current_treasury -= cost
                push!(fdf, [participation_code level_id start_treasury no_rounds user_id timestamp readable_timestamp start_approval country round_number (j - 1) population treasury current_treasury turn[j]["action"] cost turn[j]["loc"]["x"] turn[j]["loc"]["y"]])
            end
        end
    end
end
CSV.write(folder_name * ".csv", fdf)