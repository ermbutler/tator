class AnnotationCardData extends HTMLElement {
    constructor(){
        super();
    }

    init(modelData) {
        this._modelData = modelData;
        this.localizationTypes = this._modelData.getStoredLocalizationTypes();
        this.projectId = this._modelData.getProjectId();
    }

    async makeCardList(filterParams, paginationState) {
        this.cardList = {};
        this.cardList.cards = [];
        this.cardList.filterParams = filterParams;
        this.cardList.paginationState = paginationState;

        this.cardList.total = await this._modelData.getFilteredLocalizations("count", filterParams);
        this.localizations = await this._modelData.getFilteredLocalizations("objects", filterParams, paginationState.start, paginationState.stop);
        await this.getCardList(this.localizations);
        return this.cardList;
    }

    getCardList(localizations){
        return new Promise((resolve, reject) => {

            var haveCardShells = function () {
                if (counter <= 0) {
                    resolve();
                }
            }

            let counter = localizations.length;
            console.log("Processing " + counter + " localizations in gallery.");

            // Handle the case where we get nothing back
            haveCardShells();

            for(let [i, l] of localizations.entries()){
                let id = l.id;

                let entityType = this.findMetaDetails( l.meta );
                //let metaDetails = {name : "sample name", type : "sample type"};

                // #TODO Move this URL generation to _modelData
                let mediaLink = `/${this.projectId}/annotation/${l.media}`;

                let attributes = l.attributes;
                let created = new Date(l.created_datetime);
                let modified = new Date(l.modified_datetime);

                let position = i + this.cardList.paginationState.start;
                let posText = `${position + 1} of ${this.cardList.total}`;

                let card = {
                    id,
                    entityType,
                    mediaLink,
                    attributes,
                    created,
                    modified,
                    posText
                };

                this.cardList.cards.push(card);
                counter--;
                haveCardShells();

                // #TODO User list shouldn't need to be a promise and should be part
                //       of the modelData initialization
                //let promises = [
                //        this._modelData.getUser(l.modified_by),
                //        this._modelData.getLocalizationGraphic(l.id)
                //    ]

                this._modelData.getLocalizationGraphic(l.id).then((image) => {
                    this.dispatchEvent(new CustomEvent("setCardImage", {
                        composed: true,
                        detail: {
                            id: l.id,
                            image: image
                        }
                    }));
                });
            }
        });
    }

    getCardListFaster(localizations){
        //return new Promise((resolve, reject) => {

            let counter = localizations.length;
            for(let [i, l] of localizations.entries()){
                let id = l.id;

                //let metaDetails = this.findMetaDetails( l.meta );
                let metaDetails = {name : "sample name", type : "sample type"};

                let mediaLink = document.createElement("a");
                mediaLink.setAttribute("href", `/${this.projectId}/annotation/${l.media}`)
                mediaLink.innerHTML = `Media ID ${l.media}`;

                let attributes = l.attributes;
                let created = new Date(l.created_datetime);
                let modified = new Date(l.modified_datetime);

                let position = i + this.cardList.paginationState.start;
                let posText = `${position} of ${this.cardList.total}`;

                let promises = [
                        this._modelData.getUser(l.modified_by),
                        this._modelData.getLocalizationGraphic(l.id)
                    ]

                // Promise.all(promises)
                // .then((respArray) => {
                //     let userName = respArray[0].username;
                //     let graphic = respArray[1];

                    let card = {
                        id,
                        metaDetails,
                        mediaLink,
                        graphic : this._modelData.getLocalizationGraphic(l.id),
                        attributes,
                        created,
                        modified,
                        userName : this._modelData.getUser(l.modified_by),
                        posText
                    };
                    //console.log(card);
                    this.cardList.cards.push(card);
                    //counter --;
                    //console.log("counter went down is now: "+counter);
                // });

            }

            // let counterCheckout = setInterval(function(){
            //     //console.log("interval check for counter "+counter);
            //     if(counter == 0){
            //         clearInterval(counterCheckout);
            //         resolve("complete");
            //     }
            //     }, 100)

            return this.cardList;
        //});
    }

    findMetaDetails(id){
        for(let lt of this.localizationTypes){
            if(lt.id == id){
                return lt;
            }
        }
    }
}

customElements.define("annotation-card-data", AnnotationCardData);