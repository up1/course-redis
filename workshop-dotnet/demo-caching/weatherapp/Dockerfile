FROM mcr.microsoft.com/dotnet/sdk:8.0.416
WORKDIR /App
COPY . ./
RUN dotnet restore
RUN dotnet publish -c Release -o out


FROM mcr.microsoft.com/dotnet/aspnet:8.0.22
WORKDIR /App
COPY --from=0 /App/out ./
ENTRYPOINT ["dotnet", "weatherapp.dll"]